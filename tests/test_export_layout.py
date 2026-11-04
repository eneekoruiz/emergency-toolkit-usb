"""Export integration test using temporary PowerShell drives and synthetic data only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile


REPO = Path(__file__).resolve().parents[1]


class ExportLayoutTests(unittest.TestCase):
    def test_exported_scripts_resolve_payloads_and_documents(self):
        with tempfile.TemporaryDirectory(prefix="arsenal-export-") as folder:
            base = Path(folder)
            root = base / "source"
            shutil.copytree(REPO / "Arsenal_Digital", root)
            privacy, rescue = base / "privacy", base / "rescue"
            privacy.mkdir()
            rescue.mkdir()
            hardware = root / "USB_RESCATE_VENTOY/ISO/04_hardware"
            hardware.mkdir(parents=True)
            with zipfile.ZipFile(hardware / "mt86plus_fixture_x86_64.grub.iso.zip", "w") as archive:
                archive.writestr("grub-memtest.iso", b"synthetic ISO, never executable")
            (root / "SECRETS/VT_API_KEY.txt").write_text("fixture must not be exported")
            payload = root / "USB_RESCATE_VENTOY/tools/windows/fixture.dat"
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(b"fixture")
            manifest = {"assets": [{"id": "fixture", "enabled": True, "profile": "USB_RESCATE_VENTOY", "version": "1", "fileName": "fixture.dat", "destination": "USB_RESCATE_VENTOY/tools/windows", "url": "https://invalid.example/never-download", "source": "synthetic", "sha256": hashlib.sha256(b"fixture").hexdigest()}]}
            manifest["assets"].append({"id": "tails-fixture", "enabled": True, "profile": "USB_PRIVACIDAD_TAILS"})
            (root / "00_MANIFIESTOS/tools.json").write_text(json.dumps(manifest))
            wrapper = base / "test.ps1"
            wrapper.write_text(r'''
param($FixtureRoot, $Privacy, $Rescue)
$ErrorActionPreference = 'Stop'
if ((Get-PSDrive Y,Z -ErrorAction SilentlyContinue)) { throw 'Test drives already exist' }
New-PSDrive -Name Y -PSProvider FileSystem -Root $Privacy | Out-Null
New-PSDrive -Name Z -PSProvider FileSystem -Root $Rescue | Out-Null
function Resolve-Path {
    param([Parameter(Position=0)]$Path, $LiteralPath)
    $value = if ($LiteralPath) { $LiteralPath } else { $Path }
    if ($value -in @('Y:\', 'Z:\')) { return [pscustomobject]@{ProviderPath=$value;Path=$value} }
    Microsoft.PowerShell.Management\Resolve-Path -LiteralPath $value
}
function robocopy {
    param($Source, $Target, [Parameter(ValueFromRemainingArguments)]$Options)
    Get-ChildItem -LiteralPath $Source -Force | Copy-Item -Destination $Target -Recurse -Force
    $global:LASTEXITCODE = 0
}
& "$FixtureRoot/scripts/Export-ToUsb.ps1" -Root $FixtureRoot -PrivacyDrive Y:\ -RescueDrive Z:\
foreach ($relative in @('scripts/Build-Arsenal.ps1', '00_MANIFIESTOS/tools.json', 'PLAYBOOKS/recuperacion_datos_RAW.md', 'SECRETS/PROTOCOLO_BOVEDA.md', 'TESTED_BOOT_MATRIX.md', 'OPERATIONAL_ACCEPTANCE_CHECKLIST.md')) {
    if (-not (Test-Path (Join-Path $Rescue $relative))) { throw "Missing exported file: $relative" }
}
if (Test-Path "$Rescue/SECRETS/VT_API_KEY.txt") { throw 'Secret exported' }
& "$Rescue/scripts/Build-Arsenal.ps1"
if (-not (Test-Path "$Rescue/tools/windows/fixture.dat.sha256")) { throw 'Build used wrong destination' }
& "$Rescue/scripts/Expand-HardwarePayloads.ps1"
if (-not (Test-Path "$Rescue/ISO/04_hardware/grub-memtest.iso")) { throw 'Expansion used wrong destination' }
& "$Rescue/scripts/Validate-Arsenal.ps1" -SkipPayloadCheck
& "$Rescue/scripts/Verify-Arsenal.ps1"
$instructions = & "$Rescue/scripts/Get-WindowsISO.ps1" 6>&1 | Out-String
if ($instructions -notlike "*$Rescue\ISO\05_installers\windows*") { throw 'Windows ISO directory misplaced' }
& "$Rescue/scripts/New-RescueCaseLog.ps1" -CaseName fixture
if (-not (Get-ChildItem "$Rescue/case_notes" -Filter '*fixture.md')) { throw 'Case notes misplaced' }
Write-Host 'Fixture export integration OK'
''', encoding="utf-8")
            result = subprocess.run([shutil.which("pwsh") or "powershell", "-NoProfile", "-NonInteractive", "-File", str(wrapper), str(root), str(privacy), str(rescue)], capture_output=True, text=True, timeout=40)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Fixture export integration OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
