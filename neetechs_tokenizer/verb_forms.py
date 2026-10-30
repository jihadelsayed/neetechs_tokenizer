"""Conservative imperfect and imperative analysis for reviewed Form I verbs.

Unvowelled forms are ambiguous; the engine returns all compatible readings.
Only attested base stems are accepted. This is not a generative Arabic grammar.
"""
from .utils import clean_text

# root -> unprefixed imperfect core (after removing person prefix).
# These are explicitly reviewed surface spellings, not derived from perfect vowels.
IMPERFECT_CORES = {
    "كتب": "كتب", "فتح": "فتح", "درس": "درس", "عمل": "عمل",
    "حفظ": "حفظ", "فهم": "فهم", "طلب": "طلب", "شرب": "شرب",
    "سمع": "سمع", "لعب": "لعب", "علم": "علم",
}
# Surface imperative for the masculine singular; other imperative forms are
# outside the scope of this milestone.
IMPERATIVES = {
    "كتب": "اكتب", "فتح": "افتح", "درس": "ادرس",
    "عمل": "اعمل", "حفظ": "احفظ", "فهم": "افهم",
    "طلب": "اطلب", "شرب": "اشرب", "سمع": "اسمع", "لعب": "العب",
}
# person marker, ending, grammatical readings. All readings reflect ambiguity
# of UNVOWELLED surface forms. No mood assigned where vowels are missing.
IMPERFECT_RULES = (
    ("أ", "", ((1, "singular", None),)),
    ("ن", "", ((1, "plural", None),)),
    ("ي", "", ((3, "singular", "masculine"),)),
    ("ت", "", ((2, "singular", "masculine"), (3, "singular", "feminine"))),
    ("ي", "ون", ((3, "plural", "masculine"),)),
    ("ت", "ون", ((2, "plural", "masculine"),)),
    ("ت", "ين", ((2, "singular", "feminine"),)),
    ("ي", "ان", ((3, "dual", "masculine"),)),
    ("ت", "ان", ((2, "dual", None), (3, "dual", "feminine"))),
)


def analyze_imperfect(word: str) -> list[dict]:
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    surface = clean_text(word)
    result = []
    for root, core in IMPERFECT_CORES.items():
        for marker, ending, readings in IMPERFECT_RULES:
            if surface != marker + core + ending:
                continue
            for person, number, gender in readings:
                result.append({
                    "root": root, "pattern": "فعل", "stem": surface,
                    "part_of_speech": "verb", "prefixes": [],
                    "suffixes": [], "tense": "imperfect",
                    "person": person, "number": number, "gender": gender,
                    "source": "reviewed_imperfect_rules", "score": 0.87,
                })
    return result


def analyze_imperative(word: str) -> list[dict]:
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    surface = clean_text(word)
    return [
        {"root": root, "pattern": "فعل", "stem": surface,
         "part_of_speech": "verb", "prefixes": [], "suffixes": [],
         "tense": "imperative", "person": 2, "number": "singular",
         "gender": "masculine", "source": "reviewed_imperative_forms",
         "score": 0.88}
        for root, form in IMPERATIVES.items() if form == surface
    ]
