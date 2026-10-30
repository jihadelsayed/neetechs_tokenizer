"""Conservative, lexicon-validated Arabic morphological analysis.

This is a small baseline, not a general Arabic morphological parser. Unrecognized
words remain intact; we never infer a root from length or initial letters alone.
"""
from __future__ import annotations

from .utils import clean_text

from .affixes import PREFIXES, SUFFIXES
from .lexicon import generate_form, load_lexicon


def word_analyzer(word: str) -> dict:
    """Return ordered validated analyses, or an empty list for unknown words.

    The score ranks known segmentation candidates; it is not a probability.
    """
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    normalized = clean_text(word)
    if not normalized or any(ch.isspace() for ch in normalized):
        return {"word": word, "normalized": normalized, "analyses": []}
    analyses = []
    stems = load_lexicon()
    for prefix, prefix_parts, prefix_pos in PREFIXES:
        if not normalized.startswith(prefix):
            continue
        for suffix, suffix_parts, suffix_pos, suffix_labels in SUFFIXES:
            if suffix and not normalized.endswith(suffix):
                continue
            end = len(normalized) - len(suffix) if suffix else len(normalized)
            stem = normalized[len(prefix):end]
            entry = stems.get(stem)
            if entry is None:
                continue
            entries = entry
            for root, pattern, pos in entries:
                if pos not in prefix_pos or pos not in suffix_pos:
                    continue
                # Only validate the intended form, never a guessed template.
                if pattern is not None and generate_form(root, pattern) != stem:
                    continue
                analyses.append({
                    "root": root,
                    "pattern": pattern,
                    "stem": stem,
                    "part_of_speech": pos,
                    "prefixes": list(prefix_parts),
                    "suffixes": [
                        {"surface": part, "function": label}
                        for part, label in zip(suffix_parts, suffix_labels)
                    ],
                    "source": "bundled_lexicon_v1",
                    "score": round(1.0 - 0.05 * (len(prefix_parts) + len(suffix_parts)), 2),
                })
    analyses.sort(key=lambda a: (-a["score"], a["root"], a["stem"]))
    return {"word": word, "normalized": normalized, "analyses": analyses}


def wordAnalyzer(word: str) -> dict:
    """Compatibility name for the original wordAnalyzer() design."""
    return word_analyzer(word)


def get_root(word: str) -> str | None:
    """Return the highest-ranked validated root, or None if unknown."""
    analyses = word_analyzer(word)["analyses"]
    return analyses[0]["root"] if analyses else None
