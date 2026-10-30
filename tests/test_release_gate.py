"""Verify release gate cannot falsely report success."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import verify_release


class ReleaseGateTests(unittest.TestCase):
    def check(self, output, returncode=0):
        completed = type("Result", (), {"returncode": returncode, "stdout": output})()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(verify_release, "ROOT", Path(directory)):
                with patch.object(verify_release.subprocess, "run", return_value=completed):
                    captured = io.StringIO()
                    with contextlib.redirect_stdout(captured):
                        status = verify_release.main()
                    return status, captured.getvalue()

    def test_zero_tests_fail(self):
        status, out = self.check("Ran 0 tests in 0.001s\nOK")
        self.assertEqual(status, 1)
        self.assertIn("[unit_tests] FAIL", out)

    def test_nonzero_tests_pass(self):
        status, out = self.check("Ran 3 tests in 0.001s\nOK")
        self.assertEqual(status, 0)
        self.assertIn("[unit_tests] PASS", out)

    def test_no_summary_fails(self):
        status, out = self.check("OK")
        self.assertEqual(status, 1)
        self.assertIn("[unit_tests] FAIL", out)

    def test_last_summary_controls_discovery(self):
        status, out = self.check("Ran 3 tests in 0.001s\\nOK\\nRan 0 tests in 0.001s\\nOK")
        self.assertEqual(status, 1)
        self.assertIn("[unit_tests] FAIL", out)

    def test_nonzero_exit_fails(self):
        status, out = self.check("Ran 3 tests in 0.001s\nFAILED", 1)
        self.assertEqual(status, 1)
        self.assertIn("[unit_tests] FAIL", out)


if __name__ == "__main__":
    unittest.main()

class ReleaseProcessFailureTests(unittest.TestCase):
    def test_launch_failure_reported(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(verify_release, "ROOT", Path(directory)):
                with patch.object(verify_release.subprocess, "run", side_effect=OSError("blocked")):
                    with contextlib.redirect_stdout(io.StringIO()):
                        status = verify_release.main()
                report = json.loads((Path(directory) / "release-check-results.json").read_text())
        self.assertEqual(status, 1)
        self.assertFalse(report["ready_for_release_checks"])
        self.assertIn("OSError", report["checks"]["unit_tests"]["output"])

    def test_timeout_reported(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(verify_release, "ROOT", Path(directory)):
                with patch.object(verify_release.subprocess, "run", side_effect=subprocess.TimeoutExpired("unit", 120)):
                    with contextlib.redirect_stdout(io.StringIO()):
                        status = verify_release.main()
        self.assertEqual(status, 1)
