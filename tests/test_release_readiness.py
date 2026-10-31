import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_release_readiness import check_release


class ReleaseReadinessTests(unittest.TestCase):
    def test_failed_tests_skip_build_and_never_approve(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("scripts.check_release_readiness.run",
                       return_value={"passed": False, "exit_code": 1, "output": "FAIL"}) as runner:
                status = check_release(output_dir=Path(temp))
        runner.assert_called_once()
        self.assertFalse(status["code_release_checks_passed"])
        self.assertFalse(status["stable_v1_release_approved"])
        self.assertFalse(status["checks"]["wheel_build"]["passed"])

    def test_no_wheel_blocks_release(self):
        outputs = [
            {"passed": True, "exit_code": 0, "output": "OK"},
            {"passed": True, "exit_code": 0, "output": "built"},
        ]
        with tempfile.TemporaryDirectory() as temp:
            with patch("scripts.check_release_readiness.run", side_effect=outputs):
                status = check_release(output_dir=Path(temp))
        self.assertFalse(status["code_release_checks_passed"])
        self.assertFalse(status["checks"]["wheel_integrity"]["passed"])

    def test_manual_review_always_required_even_if_code_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            wheel = Path(temp) / "neetechs_tokenizer-0.9.29-py3-none-any.whl"
            wheel.write_bytes(b"test")
            with patch("scripts.check_release_readiness.run",
                       return_value={"passed": True, "exit_code": 0, "output": "OK"}):
                status = check_release(output_dir=Path(temp))
        self.assertTrue(status["code_release_checks_passed"])
        self.assertFalse(status["stable_v1_release_approved"])
        self.assertTrue(status["pending_manual_gates"])


if __name__ == "__main__":
    unittest.main()
