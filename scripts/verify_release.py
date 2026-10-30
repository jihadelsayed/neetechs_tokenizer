"""Run all release checks from the repository root, without extra packages."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("unit_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    ("morphology_regression", [sys.executable, "-m", "neetechs_tokenizer.evaluate"]),
)


def main():
    results = {}
    for name, command in CHECKS:
        try:
            proc = subprocess.run(command, cwd=ROOT, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  check=False, timeout=120)
            exit_code, output = proc.returncode, proc.stdout
        except (OSError, subprocess.TimeoutExpired) as exc:
            exit_code, output = 1, f"{type(exc).__name__}: {exc}"
        passed = exit_code == 0
        if name == "unit_tests":
            counts = re.findall(r"Ran ([0-9]+) tests?", output)
            passed = passed and bool(counts) and int(counts[-1]) > 0
        results[name] = {"passed": passed,
                         "exit_code": exit_code, "output": output[-12000:]}
        print(f"[{name}] {'PASS' if passed else 'FAIL'}", flush=True)
    report = {"ready_for_release_checks": all(x["passed"] for x in results.values()),
              "checks": results,
              "note": "Curated checks do not establish independent Arabic linguistic accuracy."}
    target = ROOT / "release-check-results.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target}")
    return 0 if report["ready_for_release_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
