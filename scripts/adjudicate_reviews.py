"""Require explicit third-party decisions for all dual-review disagreements."""
import argparse
import json
from pathlib import Path
if __package__:
    from .review_agreement import adjudicate
else:
    from review_agreement import adjudicate


def resolve_reviews(reviewer_a, reviewer_b, decisions):
    comparison = adjudicate(reviewer_a, reviewer_b)
    unresolved = {item["word"]: item for item in comparison["disagreements"]}
    if not isinstance(decisions, list):
        raise ValueError("Adjudications must be a list")
    decided = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ValueError("Invalid adjudication")
        word = decision.get("word")
        roots = decision.get("roots")
        reviewer = decision.get("adjudicator")
        rationale = decision.get("rationale")
        if word not in unresolved or word in decided:
            raise ValueError(f"Unexpected or duplicate adjudication: {word}")
        status = decision.get("status", "annotated")
        if status == "annotated":
            if not isinstance(roots, list) or not roots or any(
                not isinstance(r, str) or not r.strip() for r in roots
            ) or len(roots) != len(set(roots)):
                raise ValueError(f"Invalid adjudicated roots: {word}")
        elif status in ("uncertain", "out_of_scope"):
            if roots not in (None, []):
                raise ValueError("Excluded adjudications must not assert roots")
            roots = []
        else:
            raise ValueError(f"Invalid adjudication status: {status}")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("Missing adjudicator")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("Missing adjudication rationale")
        decided[word] = {"word": word, "roots": sorted(roots), "status": status,
                         "adjudicator": reviewer, "rationale": rationale,
                         "reviewer_a": unresolved[word]["reviewer_a"],
                         "reviewer_b": unresolved[word]["reviewer_b"]}
    missing = sorted(set(unresolved) - set(decided))
    if missing:
        raise ValueError(f"Unresolved disagreements: {missing}")
    final_cases = sorted(comparison["agreed_cases"] + [
        {"word": item["word"], "roots": item["roots"]}
        for item in decided.values() if item["status"] == "annotated"
    ], key=lambda case: case["word"])
    exclusions = sorted(comparison["agreed_exclusions"] + [
        {"word": item["word"], "status": item["status"],
         "reason": item["rationale"]}
        for item in decided.values() if item["status"] != "annotated"
    ], key=lambda case: case["word"])
    return {"schema_version": 1,
            "metadata": {"status": "adjudicated_not_independently_verified",
                         "note": "Manual provenance, reviewer independence, frozen model and holdout separation still require verification."},
            "cases": final_cases,
            "exclusions": exclusions,
            "audit": {"agreement_rate": comparison["agreement_rate"],
                      "total_reviewed": comparison["total"],
                      "included_cases": len(final_cases),
                      "excluded_cases": len(exclusions),
                      "original_disagreements": comparison["disagreements"],
                      "adjudications": list(decided.values())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("reviewer_a", "reviewer_b", "adjudications"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    def read(path):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != 1 or not isinstance(payload.get("cases"), list):
            raise ValueError(f"Invalid annotation file: {path}")
        return payload["cases"]
    result = resolve_reviews(read(args.reviewer_a), read(args.reviewer_b),
                             read(args.adjudications))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result['cases'])} adjudicated cases to {args.output}")


if __name__ == "__main__":
    main()
