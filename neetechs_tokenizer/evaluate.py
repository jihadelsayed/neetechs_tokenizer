"""Deterministic in-sample quality gate for the bundled Arabic examples.

Run: python -m neetechs_tokenizer.evaluate
Exit status 1 when any expected observation fails.
This dataset is NOT held-out and cannot establish real-world accuracy.
"""
from __future__ import annotations

import json
from importlib.resources import files
from .morphology import word_analyzer
from .tokenizer import tokenize


def evaluate_cases(cases: list[dict]) -> dict:
    if not isinstance(cases, list):
        raise TypeError("cases must be a list")
    failures = []
    positive = negative = correct_positive = correct_negative = 0
    token_checks = token_correct = 0
    for index, case in enumerate(cases):
        word = case["word"]
        analyses = word_analyzer(word)["analyses"]
        if case.get("unknown", False):
            negative += 1
            if analyses:
                failures.append({"index": index, "word": word, "reason": "false_positive"})
            else:
                correct_negative += 1
        else:
            positive += 1
            matched = any(
                a["root"] == case["root"]
                and ("pattern" not in case or a["pattern"] == case["pattern"])
                and ("tense" not in case or a.get("tense") == case["tense"])
                for a in analyses
            )
            if matched:
                correct_positive += 1
            else:
                failures.append({"index": index, "word": word, "reason": "missing_expected_analysis"})
        if "tokens" in case:
            token_checks += 1
            if tokenize(word) == case["tokens"]:
                token_correct += 1
            else:
                failures.append({"index": index, "word": word, "reason": "incorrect_segmentation"})
    total = positive + negative
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "correct_positive": correct_positive,
        "correct_negative": correct_negative,
        "token_checks": token_checks,
        "token_correct": token_correct,
        "passed": len(failures) == 0,
        "pass_rate": round((total - len({x["index"] for x in failures})) / total, 4) if total else None,
        "failures": failures,
        "note": "In-sample regression checks only; not a real-world accuracy estimate.",
    }


def load_cases() -> list[dict]:
    with files("neetechs_tokenizer").joinpath("data/regression.json").open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported regression dataset")
    return payload["cases"]


def main() -> int:
    result = evaluate_cases(load_cases())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
