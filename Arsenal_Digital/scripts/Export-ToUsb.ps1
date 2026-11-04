[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)] [string]$PrivacyDrive,
    [Parameter(Mandatory)] [string]$RescueDrive,
    [string]$Root
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $Root) { $Root = (Resolve-Path (Join-Path $ScriptRoot '..')).Path }

function Assert-DriveRoot {
    param([string]$Drive)
    if ($Drive -match '^[A-Za-z]:$') { $Drive = "$Drive\" }
    if ($Drive -notmatch '^[A-Za-z]:\\$') { throw 'Specify a mounted drive root, for example E:\, not a folder or network path.' }
    $resolved = (Resolve-Path -LiteralPath $Drive).ProviderPath
    if ($resolved -notmatch '^[A-Za-z]:\\$') { throw 'The target must resolve to a drive root.' }
    if ($resolved.TrimEnd('\') -eq $env:SystemDrive) { throw 'Refusing to export onto the Windows system drive.' }
    return $resolved
}

$privacyRoot = Assert-DriveRoot -Drive $PrivacyDrive
$rescueRoot = Assert-DriveRoot -Drive $RescueDrive
if ($privacyRoot -eq $rescueRoot) { throw 'Privacy and rescue targets must be separate mounted volumes.' }
$sourceRoot = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Root).ProviderPath)
if ($sourceRoot.StartsWith($privacyRoot, [StringComparison]::OrdinalIgnoreCase) -or $sourceRoot.StartsWith($rescueRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'The source must not reside on an export target volume.'
}

$copies = @(
    @{ Source = Join-Path $Root 'USB_PRIVACIDAD_TAILS'; Target = Join-Path $privacyRoot 'Arsenal_Digital\USB_PRIVACIDAD_TAILS' },
    @{ Source = Join-Path $Root '00_MANIFIESTOS'; Target = Join-Path $privacyRoot 'Arsenal_Digital\00_MANIFIESTOS' },
    @{ Source = Join-Path $Root 'USB_RESCATE_VENTOY'; Target = $rescueRoot },
    @{ Source = Join-Path $Root '00_MANIFIESTOS'; Target = Join-Path $rescueRoot '00_MANIFIESTOS' },
    @{ Source = Join-Path $Root 'scripts'; Target = Join-Path $rescueRoot 'scripts' },
    @{ Source = Join-Path $Root 'PLAYBOOKS'; Target = Join-Path $rescueRoot 'PLAYBOOKS' }
)

foreach ($copy in $copies) {
    if (-not (Test-Path $copy.Source)) { continue }
    if ($PSCmdlet.ShouldProcess($copy.Target, "Copy from $($copy.Source)")) {
        New-Item -ItemType Directory -Force -Path $copy.Target | Out-Null
        robocopy $copy.Source $copy.Target /E /R:2 /W:2 /NFL /NDL /NP | Out-Null
        if ($LASTEXITCODE -gt 7) { throw "Robocopy failed with code $LASTEXITCODE for $($copy.Source)" }
    }
}

foreach ($relative in @('TESTED_BOOT_MATRIX.md', 'OPERATIONAL_ACCEPTANCE_CHECKLIST.md', 'SECRETS\PROTOCOLO_BOVEDA.md')) {
    $source = Join-Path $Root $relative
    $target = Join-Path $rescueRoot $relative
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing operational document: $relative" }
    if ($PSCmdlet.ShouldProcess($target, "Copy from $source")) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
}

Write-Host 'Export complete. Re-run Verify-Arsenal.ps1 against the source before relying on payloads.'
