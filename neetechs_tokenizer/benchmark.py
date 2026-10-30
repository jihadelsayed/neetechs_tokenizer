"""Evaluate separately annotated word/root cases from JSON.

This command does not claim an independently sourced benchmark exists.
Provide a dataset prepared without using the analyzer's predictions.
Usage: python -m neetechs_tokenizer.benchmark path/to/held_out.json
"""
import argparse
import json
from pathlib import Path
from .morphology import word_analyzer


def benchmark_cases(cases):
    if not isinstance(cases, list):
        raise ValueError("Expected cases list")
    correct = 0
    supported = 0
    top_one_correct = 0
    ambiguous_top = 0
    unique_top_correct = 0
    errors = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("word"), str) or not isinstance(case.get("root"), str):
            raise ValueError(f"Case {index} requires string word and root")
        predicted = word_analyzer(case["word"])["analyses"]
        roots = {a["root"] for a in predicted}
        top_root = predicted[0]["root"] if predicted else None
        if top_root == case["root"]:
            top_one_correct += 1
        # A shared maximal score is not a confident top-1 prediction.
        # Count distinct roots only; grammatical readings of one root
        # should not be misclassified as lexical ambiguity.
        if predicted:
            best_score = predicted[0]["score"]
            top_roots = {a["root"] for a in predicted if a["score"] == best_score}
            if len(top_roots) > 1:
                ambiguous_top += 1
            elif top_root == case["root"]:
                unique_top_correct += 1
        if roots:
            supported += 1
        if case["root"] in roots:
            correct += 1
        else:
            errors.append({"index": index, "word": case["word"], "expected_root": case["root"], "predicted_roots": sorted(roots)})
    n = len(cases)
    return {"total": n, "root_recall_at_any_candidate": correct / n if n else None,
            "coverage": supported / n if n else None,
            "top_one_root_accuracy": top_one_correct / n if n else None,
            "top_one_correct": top_one_correct,
            "ambiguous_top_root_cases": ambiguous_top,
            "unambiguous_top_root_accuracy": unique_top_correct / (n - ambiguous_top) if n > ambiguous_top else None,
            "top_one_errors": n - top_one_correct,
            "errors": errors,
            "note": "Measured only against the supplied annotations. No claim of independently verified labels."}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Arabic root benchmark on an externally annotated JSON dataset")
    parser.add_argument("dataset", type=Path)
    args = parser.parse_args(argv)
    with args.dataset.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        parser.error("Dataset must be a JSON object with schema_version: 1")
    print(json.dumps(benchmark_cases(payload.get("cases")), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
