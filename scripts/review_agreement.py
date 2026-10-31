"""Blind annotation agreement gate. Never treats unreviewed seed as ground truth."""
import argparse
import json
from pathlib import Path


def adjudicate(reviews_a, reviews_b):
    """Return agreed examples and disagreements; do not call the analyzer."""
    if not isinstance(reviews_a, list) or not isinstance(reviews_b, list):
        raise ValueError("Both reviews must be lists")
    def index(reviews):
        indexed = {}
        for case in reviews:
            if not isinstance(case, dict) or not isinstance(case.get("word"), str):
                raise ValueError("Each annotation requires a word")
            word = case["word"].strip()
            if not word or word in indexed:
                raise ValueError(f"Empty or duplicate word: {word!r}")
            status = case.get("status", "annotated")
            if status == "annotated":
                roots = case.get("roots")
                if not isinstance(roots, list) or not roots or any(
                    not isinstance(root, str) or not root.strip() or root != root.strip() for root in roots
                ) or len(roots) != len(set(roots)):
                    raise ValueError(f"Invalid root annotation: {word!r}")
                if case.get("reason") is not None:
                    raise ValueError("Annotated cases cannot carry exclusion reasons")
                indexed[word] = {"status": status, "roots": sorted(roots)}
            elif status in ("uncertain", "out_of_scope"):
                if case.get("roots") not in (None, []):
                    raise ValueError("Excluded cases must not assert roots")
                reason = case.get("reason")
                if not isinstance(reason, str) or not reason.strip():
                    raise ValueError("Excluded cases require a reason")
                indexed[word] = {"status": status, "reason": reason.strip()}
            else:
                raise ValueError(f"Unsupported annotation status: {status}")
        return indexed

    first, second = index(reviews_a), index(reviews_b)
    if first.keys() != second.keys() or not first:
        raise ValueError("Reviewers must annotate the same nonempty word set")
    agreed, exclusions, disagreements = [], [], []
    for word in sorted(first):
        left, right = first[word], second[word]
        if left["status"] == right["status"] == "annotated" and left["roots"] == right["roots"]:
            agreed.append({"word": word, "roots": left["roots"]})
        elif left["status"] == right["status"] and left["status"] != "annotated":
            exclusions.append({"word": word, "status": left["status"],
                               "reviewer_a_reason": left["reason"],
                               "reviewer_b_reason": right["reason"]})
        else:
            disagreements.append({"word": word, "reviewer_a": left.get("roots", []),
                                  "reviewer_b": right.get("roots", []),
                                  "reviewer_a_status": left["status"],
                                  "reviewer_b_status": right["status"],
                                  "reviewer_a_reason": left.get("reason"),
                                  "reviewer_b_reason": right.get("reason")})
    agreement = len(agreed) + len(exclusions)
    return {"total": len(first), "agreed": agreement,
            "agreement_rate": agreement / len(first),
            "agreed_cases": agreed, "agreed_exclusions": exclusions,
            "disagreements": disagreements, "publishable_accuracy": False,
            "note": "Excluded words must be reported, not scored as rooted examples."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviewer_a", type=Path)
    parser.add_argument("reviewer_b", type=Path)
    args = parser.parse_args()
    def read(path):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            parser.error("Expected JSON with schema_version: 1")
        if not isinstance(data.get("cases"), list):
            parser.error("Expected cases list")
        return data["cases"]
    print(json.dumps(adjudicate(read(args.reviewer_a), read(args.reviewer_b)),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
