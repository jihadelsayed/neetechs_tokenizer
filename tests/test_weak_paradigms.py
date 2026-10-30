"""Coverage checks for explicitly reviewed weak-root verb forms."""
import unittest
from neetechs_tokenizer import analyze_weak_verb, wordAnalyzer
from neetechs_tokenizer.weak_forms import WEAK_VERB_FORMS


class WeakParadigmTests(unittest.TestCase):
    def test_expanded_forms(self):
        cases = {
            "قالوا": ("قول", "perfect", 3, "plural"),
            "قلنا": ("قول", "perfect", 1, "plural"),
            "يقولون": ("قول", "imperfect", 3, "plural"),
            "بعت": ("بيع", "perfect", 1, "singular"),
            "باعوا": ("بيع", "perfect", 3, "plural"),
            "نبيع": ("بيع", "imperfect", 1, "plural"),
            "دعونا": ("دعو", "perfect", 1, "plural"),
            "يدعون": ("دعو", "imperfect", 3, "plural"),
            "تدعو": ("دعو", "imperfect", 2, "singular"),
        }
        for surface, (root, tense, person, number) in cases.items():
            with self.subTest(surface=surface):
                self.assertTrue(any(
                    a["root"] == root and a["tense"] == tense
                    and a["person"] == person and a["number"] == number
                    for a in analyze_weak_verb(surface)
                ))

    def test_imperfect_ambiguity(self):
        for surface in ("تقول", "تبيع", "تدعو"):
            with self.subTest(surface=surface):
                readings = analyze_weak_verb(surface)
                self.assertEqual(
                    {(r["person"], r["gender"]) for r in readings},
                    {(2, "masculine"), (3, "feminine")},
                )

    def test_surface_lookup_is_exact(self):
        self.assertEqual(analyze_weak_verb("مقال"), [])
        self.assertEqual(analyze_weak_verb("يقولك"), [])
        self.assertEqual(analyze_weak_verb("قام"), [])

    def test_integrated_analysis(self):
        results = wordAnalyzer("قالوا")["analyses"]
        self.assertTrue(any(a.get("weak_root") and a["root"] == "قول" for a in results))

    def test_no_duplicate_records(self):
        for surface, readings in WEAK_VERB_FORMS.items():
            with self.subTest(surface=surface):
                self.assertEqual(len(readings), len(set(readings)))


if __name__ == "__main__":
    unittest.main()
