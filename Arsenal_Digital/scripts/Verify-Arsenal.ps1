[CmdletBinding()]
param(
    [string]$Root
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $Root) { $Root = (Resolve-Path (Join-Path $ScriptRoot '..')).Path }

$shaFiles = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter '*.sha256'
if (-not $shaFiles) {
    Write-Warning "No .sha256 files found under $Root"
    exit 1
}

$failures = @()
foreach ($shaFile in $shaFiles) {
    $lines = @(Get-Content -LiteralPath $shaFile.FullName | Where-Object { $_.Trim() -and -not $_.TrimStart().StartsWith('#') })
    if ($lines.Count -ne 1 -or $lines[0].Trim() -notmatch '^(?<hash>[a-fA-F0-9]{64})(?:\s+\*?(?<file>.+))?$') {
        $failures += "Invalid sha256 sidecar: $($shaFile.FullName)"
        continue
    }
    $expected = $Matches.hash.ToLowerInvariant()
    $fileName = if ($Matches.ContainsKey('file')) { $Matches.file } else { $shaFile.Name -replace '\.sha256$', '' }
    try {
        $directory = [IO.Path]::GetFullPath($shaFile.DirectoryName) + [IO.Path]::DirectorySeparatorChar
        $target = [IO.Path]::GetFullPath((Join-Path $shaFile.DirectoryName $fileName))
        if ([IO.Path]::IsPathRooted($fileName) -or -not $target.StartsWith($directory, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Sidecar target must remain inside its directory.'
        }
        $item = Get-Item -LiteralPath $target -ErrorAction Stop
        if ($item.PSIsContainer) { throw 'Expected a payload file.' }
        $ancestor = $item
        while ($ancestor) {
            if ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked payload paths are not supported.' }
            $ancestor = if ($ancestor -is [IO.DirectoryInfo]) { $ancestor.Parent } else { $ancestor.Directory }
        }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw "Hash mismatch: expected $expected actual $actual" }
        Write-Host "OK $target"
    } catch {
        $failures += "$($shaFile.FullName): $($_.Exception.Message)"
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ -ErrorAction Continue }
    exit 2
}

Write-Host 'All SHA-256 sidecars verified.'
