import unittest

from neetechs_tokenizer import get_root, tokenize, wordAnalyzer, word_analyzer
from neetechs_tokenizer.clitic_handler import split_clitics
from neetechs_tokenizer.pattern_matcher import match_pattern
from neetechs_tokenizer.utils import clean_text, is_arabic_word
from neetechs_tokenizer.lexicon import load_lexicon, validate_lexicon


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


    def test_bundled_lexicon_loaded(self):
        lexicon = load_lexicon()
        self.assertGreaterEqual(sum(len(v) for v in lexicon.values()), 35)
        self.assertEqual(len(lexicon["درس"]), 2)

    def test_more_patterns(self):
        for surface, root, pattern in [
            ("مفتاح", "فتح", "مفعال"), ("مسموع", "سمع", "مفعول"),
            ("استعمل", "عمل", "استفعل"), ("حافظ", "حفظ", "فاعل")
        ]:
            with self.subTest(surface=surface):
                analysis = word_analyzer(surface)["analyses"][0]
                self.assertEqual((analysis["root"], analysis["pattern"]), (root, pattern))

    def test_more_clitics(self):
        self.assertEqual(tokenize("والمفتاح فالمحفوظ"), ["و", "ال", "مفتاح", "ف", "ال", "محفوظ"])

    def test_invalid_schema_rejected(self):
        with self.assertRaises(ValueError):
            validate_lexicon({"schema_version": 2, "entries": []})

    def test_rootless_pattern_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_lexicon({"schema_version": 1, "entries": [
                {"surface": "كتاب", "root": "كتب", "pattern": "كتاب", "pos": "noun"}
            ]})

    def test_duplicate_placeholder_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_lexicon({"schema_version": 1, "entries": [
                {"surface": "كتبب", "root": "كتب", "pattern": "فعلل", "pos": "noun"}
            ]})

    def test_bad_pattern_rejected(self):
        with self.assertRaises(ValueError):
            validate_lexicon({"schema_version": 1, "entries": [
                {"surface": "كاتب", "root": "كتب", "pattern": "مفعول", "pos": "noun"}
            ]})

    def test_no_fabricated_new_lexical_root(self):
        self.assertEqual(word_analyzer("والمجهول")["analyses"], [])

if __name__ == "__main__":
    unittest.main()
