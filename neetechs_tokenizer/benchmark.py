"""Evaluate separately annotated word/root cases from JSON.

This command does not claim an independently sourced benchmark exists.
Provide a dataset prepared without using the analyzer's predictions.
Usage: python -m neetechs_tokenizer.benchmark path/to/held_out.json
"""
import argparse
import json
from pathlib import Path
from .morphology import word_analyzer


def _reference_roots(case, index):
    """Accept one legacy root or a nonempty collection of accepted roots."""
    has_root = "root" in case
    has_roots = "roots" in case
    if has_root == has_roots:
        raise ValueError(f"Case {index} requires exactly one of root or roots")
    raw = [case["root"]] if has_root else case["roots"]
    if not isinstance(raw, list) or not raw or any(
        not isinstance(item, str) or not item.strip() for item in raw
    ):
        raise ValueError(f"Case {index} has invalid root annotations")
    if len(raw) != len(set(raw)):
        raise ValueError(f"Case {index} has duplicate accepted roots")
    return set(raw)


def benchmark_cases(cases):
    if not isinstance(cases, list) or not cases:
        raise ValueError("Benchmark requires a nonempty cases list")
    correct = 0
    supported = 0
    top_one_correct = 0
    ambiguous_top = 0
    unique_top_correct = 0
    uniquely_ranked = 0
    tie_aware_correct = 0
    errors = []
    case_results = []
    error_counts = {"abstained": 0, "wrong_top_root": 0, "ambiguous_top_root": 0, "expected_root_missing": 0}
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("word"), str) or not case["word"].strip():
            raise ValueError(f"Case {index} requires a nonempty word")
        expected = _reference_roots(case, index)
        predicted = word_analyzer(case["word"])["analyses"]
        roots = {a["root"] for a in predicted}
        # Select among maximum-score roots, independent of input order.
        # Equal-score roots use deterministic alphabetical tie-breaking;
        # top_root_tie_cases reports where this is not evidence-based.
        best_score = max((a["score"] for a in predicted), default=None)
        top_roots = {a["root"] for a in predicted if a["score"] == best_score}
        top_root = min(top_roots) if top_roots else None
        if top_root in expected:
            top_one_correct += 1
        # A top-score tie is correct only if every tied root is accepted.
        # This avoids giving arbitrary alphabetic tie-breaking credit.
        if top_roots and top_roots <= expected:
            tie_aware_correct += 1
        # A shared maximal score is not a confident top-1 prediction.
        # Count distinct roots only; grammatical readings of one root
        # should not be misclassified as lexical ambiguity.
        if predicted:
            if len(top_roots) > 1:
                ambiguous_top += 1
            else:
                uniquely_ranked += 1
                if next(iter(top_roots)) in expected:
                    unique_top_correct += 1
        if roots:
            supported += 1
        found_expected = bool(expected & roots)
        if found_expected:
            correct += 1
        else:
            errors.append({"index": index, "word": case["word"], "expected_roots": sorted(expected), "predicted_roots": sorted(roots)})
        categories = []
        if not roots:
            categories.append("abstained")
        else:
            if top_root not in expected:
                categories.append("wrong_top_root")
            if len(top_roots) > 1 and not top_roots <= expected:
                categories.append("ambiguous_top_root")
            if not found_expected:
                categories.append("expected_root_missing")
        for category in categories:
            error_counts[category] += 1
        case_results.append({
            "index": index, "word": case["word"],
            "expected_roots": sorted(expected),
            "predicted_roots": sorted(roots),
            "top_roots": sorted(top_roots),
            "top_one_root": top_root,
            "top_one_correct": top_root in expected if top_root else False,
            "expected_in_candidates": found_expected,
            "error_categories": categories,
        })
    n = len(cases)
    return {"total": n, "root_recall_at_any_candidate": correct / n if n else None,
            "coverage": supported / n if n else None,
            "top_one_root_accuracy": top_one_correct / n if n else None,
            "top_one_correct": top_one_correct,
            "tie_aware_top_accuracy": tie_aware_correct / n if n else None,
            "tie_aware_correct": tie_aware_correct,
            "ambiguous_top_root_cases": ambiguous_top,
            "unambiguous_top_root_accuracy": unique_top_correct / uniquely_ranked if uniquely_ranked else None,
            "uniquely_ranked_cases": uniquely_ranked,
            "abstained_cases": n - supported,
            "top_root_tie_cases": ambiguous_top,
            "top_one_errors": n - top_one_correct,
            "errors": errors,
            "error_category_counts": error_counts,
            "case_results": case_results,
            "selective_accuracy": unique_top_correct / uniquely_ranked if uniquely_ranked else None,
            "selective_coverage": uniquely_ranked / n,
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
