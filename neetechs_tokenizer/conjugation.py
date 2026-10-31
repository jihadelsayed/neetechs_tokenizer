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
    # Reviewed third-person masculine singular perfect + object pronouns.
    # Do not infer subject/object roles from a bare suffix alone.
    for ending, object_label in (
        ("ه", "3ms"), ("ها", "3fs"), ("هم", "3mp"),
    ):
        if not normalized.endswith(ending):
            continue
        stem = normalized[:-len(ending)]
        for root, pattern, pos in load_lexicon().get(stem, ()):
            if pos != "verb" or pattern not in ("فعل", "استفعل"):
                continue
            results.append({
                "root": root, "pattern": pattern, "stem": stem,
                "part_of_speech": "verb", "prefixes": [],
                "suffixes": [{"surface": ending,
                              "function": "perfect_object:" + object_label}],
                "tense": "perfect", "person": 3, "number": "singular",
                "gender": "masculine", "source": "perfect_object_pronoun_rule",
                "score": 0.92,
            })
    # Unvowelled نا also permits a 3ms perfect verb + 1pl object pronoun:
    # كتبنا = katabna (we wrote) OR katabanā (he wrote us).
    # Do not force one reading without vowels or sentence context.
    if normalized.endswith("نا"):
        stem = normalized[:-2]
        for root, pattern, pos in load_lexicon().get(stem, ()):
            if pos != "verb" or pattern not in ("فعل", "استفعل"):
                continue
            results.append({
                "root": root, "pattern": pattern, "stem": stem,
                "part_of_speech": "verb", "prefixes": [],
                "suffixes": [{"surface": "نا", "function": "perfect_object:1pl"}],
                "tense": "perfect", "person": 3, "number": "singular",
                "gender": "masculine", "source": "perfect_object_pronoun_rule",
                "score": 0.92,
            })
    return results
