"""Offline regression checks; only synthetic temporary payloads are read."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "Arsenal_Digital/scripts/Verify-Arsenal.ps1"


class VerifyTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows mounted-drive guards")
    def test_export_rejects_system_drive_and_folder_even_with_whatif(self):
        script = SCRIPT.with_name("Export-ToUsb.ps1")
        system = os.environ["SystemDrive"] + "\\"
        for target in [system, str(Path(tempfile.gettempdir()))]:
            with self.subTest(target=target):
                result = subprocess.run([shutil.which("pwsh") or "powershell", "-NoProfile", "-NonInteractive", "-File", str(script), "-PrivacyDrive", target, "-RescueDrive", system, "-WhatIf"], capture_output=True, text=True, timeout=20)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Export complete", result.stdout)

    def run_case(self, content, expected, payload=b"fixture", name="payload [1].dat"):
        with tempfile.TemporaryDirectory(prefix="arsenal-verify-") as folder:
            root = Path(folder)
            (root / name).write_bytes(payload)
            if content is not None:
                (root / (name + ".sha256")).write_text(content, encoding="utf-8")
            result = subprocess.run(
                [shutil.which("pwsh") or "powershell", "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), "-Root", folder],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_named_literal_path_and_hash_only(self):
        digest = hashlib.sha256(b"fixture").hexdigest()
        for sidecar in [digest, f"{digest} *payload [1].dat", f"# checksum\n{digest}  payload [1].dat\n"]:
            with self.subTest(sidecar=sidecar):
                self.run_case(sidecar, 0)

    def test_tampered_missing_malformed_and_outside_directory(self):
        digest = hashlib.sha256(b"fixture").hexdigest()
        for sidecar in ["0" * 64, "invalid", f"{digest} *missing.dat", f"{digest} *../outside.dat", f"{digest}\n{digest}"]:
            with self.subTest(sidecar=sidecar):
                self.run_case(sidecar, 2)

    def test_no_sidecars_is_not_success(self):
        self.run_case(None, 1)


if __name__ == "__main__":
    unittest.main()
