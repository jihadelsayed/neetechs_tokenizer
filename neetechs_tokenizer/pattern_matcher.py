"""Backwards-compatible, lexicon-validated pattern matching API."""
from .morphology import word_analyzer


def match_pattern(word: str, root: str) -> str | None:
    for analysis in word_analyzer(word)["analyses"]:
        if analysis["root"] == root:
            return analysis["pattern"]
    return None
