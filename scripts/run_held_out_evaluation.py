"""Run held-out root evaluation with dataset provenance and source pinning.

This command deliberately does not claim independent accuracy certification.
"""
import argparse
import json
import subprocess
from pathlib import Path

from neetechs_tokenizer.benchmark import benchmark_cases
from scripts.verify_evaluation_provenance import verify_provenance


def frozen_source_revision():
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
        check=True, timeout=15,
    )
    return process.stdout.strip()


def run_evaluation(dataset, manifest, *, revision=None):
    verified = verify_provenance(dataset, manifest)
    actual_revision = revision if revision is not None else frozen_source_revision()
    if actual_revision != verified["frozen_commit"]:
        raise ValueError(
            f"Analyzer revision differs from frozen commit: "
            f"{actual_revision} != {verified['frozen_commit']}"
        )
    payload = json.loads(Path(dataset).read_text(encoding="utf-8"))
    results = benchmark_cases(payload["cases"])
    return {
        "evaluation_kind": "held_out_reviewed_provenance_declared",
        "independent_accuracy_verified": False,
        "dataset_sha256": verified["dataset_sha256"],
        "frozen_commit": actual_revision,
        "manifest_valid": verified["manifest_valid"],
        "metrics": results,
        "note": "Review independence and holdout separation require external verification."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_evaluation(args.dataset, args.manifest)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
