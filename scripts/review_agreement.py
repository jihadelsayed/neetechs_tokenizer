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
            roots = case.get("roots")
            if not word or not isinstance(roots, list) or not roots or any(
                not isinstance(root, str) or not root.strip() for root in roots
            ) or len(roots) != len(set(roots)):
                raise ValueError(f"Invalid root annotation: {word!r}")
            if word in indexed:
                raise ValueError(f"Duplicate word: {word}")
            indexed[word] = set(roots)
        return indexed

    first, second = index(reviews_a), index(reviews_b)
    if first.keys() != second.keys() or not first:
        raise ValueError("Reviewers must annotate the same nonempty word set")
    agreed, disagreements = [], []
    for word in sorted(first):
        if first[word] == second[word]:
            agreed.append({"word": word, "roots": sorted(first[word])})
        else:
            disagreements.append({"word": word, "reviewer_a": sorted(first[word]),
                                  "reviewer_b": sorted(second[word])})
    return {"total": len(first), "agreed": len(agreed),
            "agreement_rate": len(agreed) / len(first),
            "agreed_cases": agreed, "disagreements": disagreements,
            "publishable_accuracy": False,
            "note": "Agreement alone does not prove independence or adjudicate disagreements."}


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
