"""Tokenization invariants across mixed text and unknown Arabic forms."""
import unittest

from neetechs_tokenizer import tokenize
from neetechs_tokenizer.candidates import priority_identifier
from neetechs_tokenizer.utils import clean_text


class TokenizationInvariants(unittest.TestCase):
    def test_lossless_known_words(self):
        for word in ("والكاتب", "بالكتاب", "استكتبوهم", "كتبوا", "مكتوب"):
            with self.subTest(word=word):
                self.assertEqual("".join(tokenize(word)), clean_text(word))

    def test_unknown_words_are_preserved(self):
        for word in ("وليد", "والورد", "كلمةغيرمعروفة", "المدرسة"):
            with self.subTest(word=word):
                self.assertEqual(tokenize(word), [word])

    def test_punctuation_not_deleted(self):
        self.assertEqual(tokenize("مكتوب!"), ["مكتوب", "!"])
        self.assertEqual(tokenize("والكاتب،"), ["و", "ال", "كاتب", "،"])

    def test_mixed_text(self):
        self.assertEqual(tokenize("مكتوب Python 3"), ["مكتوب", "Python", "3"])

    def test_all_candidates_reconstruct_surface(self):
        for word in ("بالكتاب", "استكتبوهم", "كلمةغيرمعروفة"):
            for candidate in priority_identifier(word):
                self.assertEqual(
                    "".join(candidate.prefixes) + candidate.stem +
                    "".join(candidate.suffixes), word)

    def test_empty_input(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   "), [])


if __name__ == "__main__":
    unittest.main()
