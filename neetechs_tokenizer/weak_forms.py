"""Reviewed surface forms for three soundly attested Arabic weak roots.

Not a productive weak-root conjugator: each form is explicitly whitelisted.
Unvowelled ambiguity is preserved. Avoid assigning vowel-dependent mood.
"""
from collections import defaultdict
from .utils import clean_text

# surface, root, tense, person, number, gender
_REVIEWED = (
    ("قال", "قول", "perfect", 3, "singular", "masculine"),
    ("قلت", "قول", "perfect", 1, "singular", None),
    ("قلت", "قول", "perfect", 2, "singular", "masculine"),
    ("قلت", "قول", "perfect", 2, "singular", "feminine"),
    ("يقول", "قول", "imperfect", 3, "singular", "masculine"),
    ("قل", "قول", "imperative", 2, "singular", "masculine"),
    ("باع", "بيع", "perfect", 3, "singular", "masculine"),
    ("يبيع", "بيع", "imperfect", 3, "singular", "masculine"),
    ("بع", "بيع", "imperative", 2, "singular", "masculine"),
    ("دعا", "دعو", "perfect", 3, "singular", "masculine"),
    ("يدعو", "دعو", "imperfect", 3, "singular", "masculine"),
    ("ادع", "دعو", "imperative", 2, "singular", "masculine"),
    ("قالوا", "قول", "perfect", 3, "plural", "masculine"),
    ("قالا", "قول", "perfect", 3, "dual", "masculine"),
    ("قالت", "قول", "perfect", 3, "singular", "feminine"),
    ("قلنا", "قول", "perfect", 1, "plural", None),
    ("قلتم", "قول", "perfect", 2, "plural", "masculine"),
    ("يقولون", "قول", "imperfect", 3, "plural", "masculine"),
    ("تقولون", "قول", "imperfect", 2, "plural", "masculine"),
    ("تقول", "قول", "imperfect", 2, "singular", "masculine"),
    ("تقول", "قول", "imperfect", 3, "singular", "feminine"),
    ("نقول", "قول", "imperfect", 1, "plural", None),
    ("أقول", "قول", "imperfect", 1, "singular", None),
    ("باعوا", "بيع", "perfect", 3, "plural", "masculine"),
    ("باعا", "بيع", "perfect", 3, "dual", "masculine"),
    ("باعت", "بيع", "perfect", 3, "singular", "feminine"),
    ("بعنا", "بيع", "perfect", 1, "plural", None),
    ("بعت", "بيع", "perfect", 1, "singular", None),
    ("بعت", "بيع", "perfect", 2, "singular", "masculine"),
    ("بعت", "بيع", "perfect", 2, "singular", "feminine"),
    ("يبيعون", "بيع", "imperfect", 3, "plural", "masculine"),
    ("تبيع", "بيع", "imperfect", 2, "singular", "masculine"),
    ("تبيع", "بيع", "imperfect", 3, "singular", "feminine"),
    ("تبيعون", "بيع", "imperfect", 2, "plural", "masculine"),
    ("نبيع", "بيع", "imperfect", 1, "plural", None),
    ("أبيع", "بيع", "imperfect", 1, "singular", None),
    ("دعوا", "دعو", "perfect", 3, "plural", "masculine"),
    ("دعت", "دعو", "perfect", 3, "singular", "feminine"),
    ("دعوت", "دعو", "perfect", 1, "singular", None),
    ("دعوت", "دعو", "perfect", 2, "singular", "masculine"),
    ("دعوت", "دعو", "perfect", 2, "singular", "feminine"),
    ("دعونا", "دعو", "perfect", 1, "plural", None),
    ("يدعون", "دعو", "imperfect", 3, "plural", "masculine"),
    ("تدعو", "دعو", "imperfect", 2, "singular", "masculine"),
    ("تدعو", "دعو", "imperfect", 3, "singular", "feminine"),
    ("تدعون", "دعو", "imperfect", 2, "plural", "masculine"),
    ("ندعو", "دعو", "imperfect", 1, "plural", None),
    ("أدعو", "دعو", "imperfect", 1, "singular", None),
)


def _build_index():
    result = defaultdict(list)
    for surface, root, tense, person, number, gender in _REVIEWED:
        entry = (root, "I", tense, person, number, gender)
        if entry in result[surface]:
            raise ValueError("Duplicate weak verb record: " + surface)
        result[surface].append(entry)
    return dict(result)


WEAK_VERB_FORMS = _build_index()


def analyze_weak_verb(word: str) -> list[dict]:
    """Analyze exact reviewed surfaces; never invent weak-root matches."""
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    surface = clean_text(word)
    return [
        {
            "root": root, "pattern": "فعل", "stem": surface,
            "part_of_speech": "verb", "prefixes": [], "suffixes": [],
            "tense": tense, "person": person, "number": number,
            "gender": gender, "weak_root": True, "verb_form": form,
            "source": "attested_weak_verb_form", "score": 0.93,
        }
        for root, form, tense, person, number, gender
        in WEAK_VERB_FORMS.get(surface, ())
    ]
