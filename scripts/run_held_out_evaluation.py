"""Run held-out root evaluation with dataset provenance and source pinning.

This command deliberately does not claim independent accuracy certification.
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from neetechs_tokenizer.benchmark import benchmark_cases
from scripts.verify_evaluation_provenance import verify_provenance


def frozen_source_revision():
    """Identify the exact checkout and reject any uncommitted source changes."""
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, check=True, timeout=15,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--",
         "neetechs_tokenizer", "scripts", "setup.py"],
        cwd=ROOT, capture_output=True, text=True, check=True, timeout=15,
    ).stdout
    if status.strip():
        raise ValueError("Analyzer checkout has uncommitted source changes")
    return revision


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
    cases = payload["cases"]
    exclusions = payload.get("exclusions", [])
    audit = payload.get("audit", {})
    if not isinstance(exclusions, list) or not isinstance(audit, dict):
        raise ValueError("Invalid evaluation exclusions or audit")
    if not isinstance(audit.get("total_reviewed"), int) or isinstance(audit.get("total_reviewed"), bool):
        # Reject legacy datasets with unknown exclusions: denominator cannot be trusted.
        raise ValueError("Missing original total_reviewed denominator")
    if not isinstance(audit.get("included_cases"), int) or isinstance(audit.get("included_cases"), bool):
        raise ValueError("Missing included_cases count")
    if not isinstance(audit.get("excluded_cases"), int) or isinstance(audit.get("excluded_cases"), bool):
        raise ValueError("Missing excluded_cases count")
    total = audit["total_reviewed"]
    if total <= 0 or audit["included_cases"] != len(cases) or audit["excluded_cases"] != len(exclusions) or total != len(cases) + len(exclusions):
        raise ValueError("Review counts do not reconcile with cases and exclusions")
    words = [x.get("word") for x in cases + exclusions if isinstance(x, dict)]
    if len(words) != total or any(not isinstance(w, str) or not w.strip() for w in words) or len(set(words)) != total:
        raise ValueError("Missing, duplicated or malformed reviewed words")
    for exclusion in exclusions:
        if exclusion.get("status") not in ("uncertain", "out_of_scope") or exclusion.get("roots") not in (None, []):
            raise ValueError("Invalid excluded word status or roots")
        if not (exclusion.get("reason") or
                (exclusion.get("reviewer_a_reason") and exclusion.get("reviewer_b_reason"))):
            raise ValueError("Excluded word is missing reviewer reasons")
    review_metrics = {
        "total_reviewed": total,
        "included_cases": len(cases),
        "excluded_cases": len(exclusions),
        "annotation_inclusion_rate": len(cases) / total,
        "analyzer_coverage_of_all_reviewed": (results["coverage"] * len(cases)) / total,
        "top_one_correct_of_all_reviewed": results["top_one_correct"] / total,
        "excluded_words": [{"word": x["word"], "status": x["status"]} for x in exclusions],
        "note": "Excluded cases are not scored; these rates use all originally reviewed words."
    }
    return {
        "evaluation_kind": "held_out_reviewed_provenance_declared",
        "independent_accuracy_verified": False,
        "dataset_sha256": verified["dataset_sha256"],
        "frozen_commit": actual_revision,
        "manifest_valid": verified["manifest_valid"],
        "metrics": results,
        "review_metrics": review_metrics,
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
