import unittest

from neetechs_tokenizer import get_root, tokenize, wordAnalyzer, word_analyzer
from neetechs_tokenizer.clitic_handler import split_clitics
from neetechs_tokenizer.pattern_matcher import match_pattern
from neetechs_tokenizer.utils import clean_text, is_arabic_word


class ArabicTokenizerTests(unittest.TestCase):
    def test_triliteral_pattern(self):
        a = word_analyzer("مكتوب")["analyses"][0]
        self.assertEqual((a["root"], a["pattern"]), ("كتب", "مفعول"))

    def test_form_x_is_not_form_viii(self):
        a = wordAnalyzer("استكتب")["analyses"][0]
        self.assertEqual((a["root"], a["pattern"]), ("كتب", "استفعل"))
        self.assertEqual(match_pattern("استكتب", "كتب"), "استفعل")

    def test_plural_subject_and_object(self):
        a = word_analyzer("استكتبوهم")["analyses"][0]
        self.assertEqual(a["root"], "كتب")
        self.assertEqual([s["surface"] for s in a["suffixes"]], ["و", "هم"])
        self.assertEqual(tokenize("استكتبوهم"), ["استكتب", "و", "هم"])

    def test_plural_alif(self):
        self.assertEqual(tokenize("كتبوا"), ["كتب", "وا"])

    def test_attached_article(self):
        self.assertEqual(tokenize("والكاتب بالكتاب"), ["و", "ال", "كاتب", "ب", "ال", "كتاب"])

    def test_sentence_and_punctuation(self):
        self.assertEqual(tokenize("استكتب المعلم الطالب الدرس!"),
                         ["استكتب", "ال", "معلم", "ال", "طالب", "ال", "درس", "!"])

    def test_unknowns_not_split(self):
        self.assertEqual(tokenize("وليد والورد"), ["وليد", "والورد"])
        self.assertEqual(word_analyzer("وليد")["analyses"], [])
        self.assertIsNone(get_root("مدرسة"))

    def test_preserve_significant_characters(self):
        self.assertEqual(clean_text("مَدْرَسَةٌ فَتَى"), "مدرسة فتى")
        self.assertTrue(is_arabic_word("مُعَلِّم"))
        self.assertFalse(is_arabic_word(""))

    def test_no_splitting_for_surface_mode(self):
        self.assertEqual(tokenize("والكاتب!", split_clitics=False), ["والكاتب", "!"])

    def test_clitics_compatibility(self):
        self.assertEqual(split_clitics("والكاتب"), ["و", "ال", "كاتب"])

    def test_invalid_inputs(self):
        with self.assertRaises(TypeError):
            word_analyzer(None)
        with self.assertRaises(TypeError):
            tokenize(None)

    def test_word_analysis_does_not_fabricate_roots(self):
        self.assertIsNone(get_root("المدرسة"))
        self.assertEqual(get_root("مكتوب"), "كتب")


if __name__ == "__main__":
    unittest.main()
