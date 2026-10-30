import unittest
from unittest.mock import patch

from neetechs_tokenizer import get_root


class StrictRootTests(unittest.TestCase):
    def test_known_unique(self):
        self.assertEqual(get_root("مكتوب", require_unique=True), "كتب")

    def test_unknown_abstains(self):
        self.assertIsNone(get_root("كلمةغيرمعروفة", require_unique=True))

    def test_tied_distinct_roots_abstain_only_in_strict_mode(self):
        analyses = [
            {"root": "كتب", "score": 0.9},
            {"root": "كبت", "score": 0.9},
        ]
        with patch("neetechs_tokenizer.morphology.word_analyzer",
                   return_value={"analyses": analyses}):
            self.assertEqual(get_root("example"), "كتب")
            self.assertIsNone(get_root("example", require_unique=True))

    def test_same_root_multiple_grammar_readings_not_ambiguous(self):
        analyses = [{"root": "كتب", "score": 0.9},
                    {"root": "كتب", "score": 0.9}]
        with patch("neetechs_tokenizer.morphology.word_analyzer",
                   return_value={"analyses": analyses}):
            self.assertEqual(get_root("example", require_unique=True), "كتب")

    def test_lower_score_competitor_does_not_force_abstention(self):
        analyses = [{"root": "كتب", "score": 0.9},
                    {"root": "علم", "score": 0.8}]
        with patch("neetechs_tokenizer.morphology.word_analyzer",
                   return_value={"analyses": analyses}):
            self.assertEqual(get_root("example", require_unique=True), "كتب")


if __name__ == "__main__":
    unittest.main()
