"""Check both public evaluation command entry points without reviewer data."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvaluationEntrypointTests(unittest.TestCase):
    def test_direct_script_help(self):
        proc = subprocess.run(
            [sys.executable, "scripts/run_held_out_evaluation.py", "--help"],
            cwd=ROOT, capture_output=True, text=True, timeout=20
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dataset", proc.stdout)
        self.assertIn("manifest", proc.stdout)

    def test_module_help(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.run_held_out_evaluation", "--help"],
            cwd=ROOT, capture_output=True, text=True, timeout=20
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dataset", proc.stdout)
        self.assertIn("manifest", proc.stdout)


if __name__ == "__main__":
    unittest.main()
