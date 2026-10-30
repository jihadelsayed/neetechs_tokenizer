"""Small attested weak-root paradigm table.

Do not generalize sound-root replacement rules to weak verbs. Orthographic
alternations require lexeme-specific paradigms and full vowel information.
"""
from .utils import clean_text

# (root, verb form, tense, person, number, gender).
# These entries represent individual reviewed undiacritized surfaces.
WEAK_VERB_FORMS = {
    "قال": [("قول", "I", "perfect", 3, "singular", "masculine")],
    "قلت": [("قول", "I", "perfect", 1, "singular", None),
           ("قول", "I", "perfect", 2, "singular", "masculine"),
           ("قول", "I", "perfect", 2, "singular", "feminine")],
    "يقول": [("قول", "I", "imperfect", 3, "singular", "masculine")],
    "قل": [("قول", "I", "imperative", 2, "singular", "masculine")],
    "باع": [("بيع", "I", "perfect", 3, "singular", "masculine")],
    "يبيع": [("بيع", "I", "imperfect", 3, "singular", "masculine")],
    "بع": [("بيع", "I", "imperative", 2, "singular", "masculine")],
    "دعا": [("دعو", "I", "perfect", 3, "singular", "masculine")],
    "يدعو": [("دعو", "I", "imperfect", 3, "singular", "masculine")],
    "ادع": [("دعو", "I", "imperative", 2, "singular", "masculine")],
}


def analyze_weak_verb(word: str) -> list[dict]:
    """Match exact attested surfaces; return [] for unsupported words."""
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    normalized = clean_text(word)
    return [
        {"root": root, "pattern": "فعل", "stem": normalized,
         "part_of_speech": "verb", "prefixes": [], "suffixes": [],
         "tense": tense, "person": person, "number": number,
         "gender": gender, "weak_root": True,
         "verb_form": form, "source": "attested_weak_verb_form",
         "score": 0.93}
        for root, form, tense, person, number, gender
        in WEAK_VERB_FORMS.get(normalized, [])
    ]
