"""Contract tests for all public word analyses, including ambiguity."""
import unittest

from neetechs_tokenizer import word_analyzer, tokenize


class AnalyzerContractTests(unittest.TestCase):
    def test_all_analyses_reconstruct_input(self):
        words = (
            "استكتبوهم", "بالكتاب", "والكاتب", "كتبت", "كتبوا",
            "يكتب", "تكتب", "قال", "قلت", "يقولون", "تدعو",
            "الكاتبهم", "وليد", "مكتوب",
        )
        for word in words:
            for analysis in word_analyzer(word)["analyses"]:
                with self.subTest(word=word, source=analysis["source"]):
                    joined = ("".join(analysis["prefixes"]) + analysis["stem"]
                              + "".join(s["surface"] for s in analysis["suffixes"]))
                    self.assertEqual(joined, word)

    def test_preserve_unknown(self):
        self.assertEqual(word_analyzer("كلمةغيرمعروفة")["analyses"], [])
        self.assertEqual(tokenize("كلمةغيرمعروفة"), ["كلمةغيرمعروفة"])

    def test_no_internal_split_on_imperfect(self):
        analyses = word_analyzer("تكتب")["analyses"]
        self.assertTrue(any(a.get("tense") == "imperfect" for a in analyses))
        self.assertTrue(all(
            "".join(a["prefixes"]) + a["stem"]
            + "".join(s["surface"] for s in a["suffixes"]) == "تكتب"
            for a in analyses
        ))


if __name__ == "__main__":
    unittest.main()
