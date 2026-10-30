"""Conservative perfect-tense analysis of attested sound-root verb stems.

Unvowelled Arabic creates ambiguous person/gender readings; preserve them all.
"""
from .lexicon import load_lexicon
from .utils import clean_text

PERFECT_SUFFIXES = (
    ("", ((3, "singular", "masculine"),)),
    ("ت", ((1, "singular", None), (2, "singular", "masculine"),
           (2, "singular", "feminine"), (3, "singular", "feminine"))),
    ("نا", ((1, "plural", None),)),
    ("تم", ((2, "plural", "masculine"),)),
    ("تن", ((2, "plural", "feminine"),)),
    ("تما", ((2, "dual", None),)),
    ("وا", ((3, "plural", "masculine"),)),
    ("ن", ((3, "plural", "feminine"),)),
    ("ا", ((3, "dual", "masculine"),)),
    ("تا", ((3, "dual", "feminine"),)),
)


def analyze_perfect(word: str) -> list[dict]:
    """Return reviewed-stem candidates; no arbitrary root extraction."""
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    normalized = clean_text(word)
    results = []
    for ending, readings in PERFECT_SUFFIXES:
        if ending and not normalized.endswith(ending):
            continue
        stem = normalized[:-len(ending)] if ending else normalized
        for root, pattern, pos in load_lexicon().get(stem, ()):
            if pos != "verb" or pattern not in ("فعل", "استفعل"):
                continue
            for person, number, gender in readings:
                results.append({
                    "root": root, "pattern": pattern, "stem": stem,
                    "part_of_speech": "verb", "prefixes": [],
                    "suffixes": ([{"surface": ending, "function": "perfect_subject"}]
                                 if ending else []),
                    "tense": "perfect", "person": person, "number": number,
                    "gender": gender, "source": "perfect_conjugation_rule",
                    "score": 0.92 if ending else 0.89,
                })
    return results
