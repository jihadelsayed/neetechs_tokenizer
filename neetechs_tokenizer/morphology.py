"""Conservative, lexicon-validated Arabic morphological analysis.

This is a small baseline, not a general Arabic morphological parser. Unrecognized
words remain intact; we never infer a root from length or initial letters alone.
"""
from __future__ import annotations

from .utils import clean_text

# A curated starter lexicon. Keys are *unvowelled surface stems*. Templates use
# ف/ع/ل for the three radicals. Extend data only with reviewed analyses.
STEMS = {
    "كتب": ("كتب", "فعل", "verb"),
    "كاتب": ("كتب", "فاعل", "noun"),
    "مكتوب": ("كتب", "مفعول", "noun"),
    "كتاب": ("كتب", "فعال", "noun"),
    "كتابة": ("كتب", "فعالة", "noun"),
    "استكتب": ("كتب", "استفعل", "verb"),
    "علم": ("علم", "فعل", "verb"),
    "عالم": ("علم", "فاعل", "noun"),
    "معلوم": ("علم", "مفعول", "noun"),
    "تعليم": ("علم", "تفعيل", "noun"),
    "درس": (("درس", "فعل", "noun"), ("درس", "فعل", "verb")),
    "دارس": ("درس", "فاعل", "noun"),
    "مدروس": ("درس", "مفعول", "noun"),
    "طالب": ("طلب", "فاعل", "noun"),
    "معلم": ("علم", "مفعل", "noun"),  # Simplified unvowelled template
}

# (written surface, segmented pieces, compatible parts of speech)
PREFIXES = (
    ("", (), ("noun", "verb")),
    ("و", ("و",), ("noun", "verb")),
    ("ف", ("ف",), ("noun", "verb")),
    ("ال", ("ال",), ("noun",)),
    ("وال", ("و", "ال"), ("noun",)),
    ("فال", ("ف", "ال"), ("noun",)),
    ("ب", ("ب",), ("noun",)),
    ("ل", ("ل",), ("noun",)),
    ("ك", ("ك",), ("noun",)),
    ("بال", ("ب", "ال"), ("noun",)),
    ("كال", ("ك", "ال"), ("noun",)),
    ("س", ("س",), ("verb",)),
    ("وس", ("و", "س"), ("verb",)),
)

# (written suffix, segments, compatible parts of speech, labels)
SUFFIXES = (
    ("", (), ("noun", "verb"), ()),
    ("وا", ("وا",), ("verb",), ("subject:3mp",)),
    # Before an attached object pronoun, plural alif is normally absent.
    ("وهم", ("و", "هم"), ("verb",), ("subject:3mp", "object:3mp")),
    ("هم", ("هم",), ("noun", "verb"), ("possessive-or-object:3mp",)),
    ("ها", ("ها",), ("noun", "verb"), ("possessive-or-object:3fs",)),
)


def generate_form(root: str, pattern: str) -> str:
    """Render a sound triliteral root into an unvowelled template."""
    if len(root) != 3:
        raise ValueError("Only triliteral roots are supported")
    return "".join(dict(zip("فعل", root)).get(c, c) for c in pattern)


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
    for prefix, prefix_parts, prefix_pos in PREFIXES:
        if not normalized.startswith(prefix):
            continue
        for suffix, suffix_parts, suffix_pos, suffix_labels in SUFFIXES:
            if suffix and not normalized.endswith(suffix):
                continue
            end = len(normalized) - len(suffix) if suffix else len(normalized)
            stem = normalized[len(prefix):end]
            entry = STEMS.get(stem)
            if entry is None:
                continue
            entries = entry if isinstance(entry[0], tuple) else (entry,)
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
                    "source": "starter_lexicon",
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
