"""Shared morphology rules must agree across candidate and final analysis."""
import unittest

from neetechs_tokenizer import priority_identifier, word_analyzer
from neetechs_tokenizer.validation import (
    compatible_affixes, reconstructs_surface, valid_analysis,
)


class SharedValidationTests(unittest.TestCase):
    def test_article_noun_and_possessive_rejection(self):
        self.assertTrue(compatible_affixes(("و", "ال"), (), "noun"))
        self.assertFalse(compatible_affixes(("ال",), (), "verb"))
        self.assertFalse(compatible_affixes(("ال",), ("possessive-or-object:3ms",), "noun"))
        self.assertTrue(compatible_affixes((), ("possessive-or-object:3ms",), "noun"))

    def test_lossless_reconstruction(self):
        self.assertTrue(reconstructs_surface("وبالكتاب", ("و", "ب", "ال"),
                                             "كتاب", ()))
        self.assertFalse(reconstructs_surface("وبالكتاب", ("و", "ال"),
                                              "كتاب", ()))
        self.assertFalse(reconstructs_surface("كتاب", (), "", ("كتاب",)))

    def test_both_past_tense_na_readings_remain(self):
        analyses = [a for a in word_analyzer("كتبنا")["analyses"]
                    if a.get("tense") == "perfect"]
        functions = {a["suffixes"][0]["function"] for a in analyses}
        self.assertIn("perfect_subject", functions)
        self.assertIn("perfect_object:1pl", functions)
        self.assertTrue(all(valid_analysis("كتبنا", a) for a in analyses))

    def test_article_possessive_filtered_in_all_paths(self):
        for word in ("الكاتبهم", "بالكتابه", "وبالكتابهم"):
            with self.subTest(word=word):
                for candidate in priority_identifier(word):
                    self.assertFalse(
                        "ال" in candidate.prefixes and
                        any(label.startswith("possessive-or-object:")
                            for label in candidate.labels))
                self.assertEqual(word_analyzer(word)["analyses"], [])

    def test_all_results_are_lossless(self):
        for word in ("استكتبوهم", "والكاتب", "كتبنا", "كتبها",
                     "اكتبوا", "فكالمفتاح", "يكتب"):
            with self.subTest(word=word):
                self.assertTrue(all(valid_analysis(word, analysis)
                                    for analysis in word_analyzer(word)["analyses"]))


if __name__ == "__main__":
    unittest.main()
