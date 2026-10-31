"""Fail-closed local release-candidate readiness report (never publishes)."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(command):
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False, timeout=300)
    return {"passed": result.returncode == 0, "exit_code": result.returncode,
            "output": result.stdout[-6000:]}


def check_release(*, output_dir=None):
    destination = output_dir or ROOT / "dist"
    destination.mkdir(parents=True, exist_ok=True)
    # Enforce freshness for both CLI and direct Python callers.
    if any(destination.glob("neetechs_tokenizer-*.whl")):
        raise ValueError("Output directory already has matching wheels; use a clean directory")
    checks = {}
    checks["release_tests"] = run([sys.executable, "scripts/verify_release.py"])
    if checks["release_tests"]["passed"]:
        checks["wheel_build"] = run([
            sys.executable, "-m", "pip", "wheel", ".", "--no-deps",
            "--no-build-isolation", "--wheel-dir", str(destination)
        ])
    else:
        checks["wheel_build"] = {"passed": False, "skipped": "release tests failed"}
    wheels = sorted(destination.glob("neetechs_tokenizer-*.whl"))
    # Reusing old wheels would produce misleading readiness. Require a clean
    # output directory, with no existing matching distribution before the run.
    if checks["wheel_build"]["passed"] and len(wheels) == 1:
        wheel = wheels[0]
        checks["wheel_integrity"] = run(
            [sys.executable, "scripts/check_wheel.py", str(wheel)])
        if checks["wheel_integrity"]["passed"]:
            checks["installed_smoke"] = run(
                [sys.executable, "scripts/smoke_installed_wheel.py", str(wheel)])
        else:
            checks["installed_smoke"] = {"passed": False, "skipped": "wheel integrity failed"}
    else:
        checks["wheel_integrity"] = {"passed": False, "skipped": "wheel not built or ambiguous"}
        checks["installed_smoke"] = {"passed": False, "skipped": "wheel not verified"}
    code_ready = all(checks[k]["passed"] for k in checks)
    return {"code_release_checks_passed": code_ready,
            "stable_v1_release_approved": False,
            "pending_manual_gates": [
                "Independent Arabic linguistic validation",
                "Document supported linguistic coverage and known limitations",
                "Human approval of version and publication"
            ], "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    destination = (args.output_dir or ROOT / "dist").resolve()
    if any(destination.glob("neetechs_tokenizer-*.whl")):
        parser.error("Output directory already has matching wheels; use a clean directory")
    try:
        report = check_release(output_dir=destination)
    except (OSError, subprocess.TimeoutExpired) as exc:
        report = {"code_release_checks_passed": False,
                  "stable_v1_release_approved": False,
                  "error": str(exc)}
    output = ROOT / "release-readiness-results.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["code_release_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
