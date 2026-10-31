import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.smoke_installed_wheel import run_wheel_smoke


class InstalledWheelSmokeTests(unittest.TestCase):
    def test_rejects_non_wheel_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.zip"
            path.write_bytes(b"placeholder")
            with self.assertRaisesRegex(ValueError, ".whl"):
                run_wheel_smoke(path)

    def test_missing_wheel_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                run_wheel_smoke(Path(directory) / "missing.whl")

    def test_propagates_install_failure(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.whl"
            path.write_bytes(b"placeholder")
            with patch("scripts.smoke_installed_wheel.venv.EnvBuilder") as builder:
                with patch("scripts.smoke_installed_wheel.subprocess.run",
                           side_effect=subprocess.CalledProcessError(1, "pip")):
                    with self.assertRaises(subprocess.CalledProcessError):
                        run_wheel_smoke(path)
            builder.assert_called_once()


if __name__ == "__main__":
    unittest.main()
