import unittest
from neetechs_tokenizer import analyze_text


class SentenceAnalysisTests(unittest.TestCase):
    def test_words_and_punctuation(self):
        result = analyze_text("مكتوب، مجهول!")
        self.assertEqual([r["token"] for r in result], ["مكتوب", "،", "مجهول", "!"])
        self.assertTrue(any(a["root"] == "كتب" for a in result[0]["analyses"]))
        self.assertEqual(result[1]["analyses"], [])
        self.assertEqual(result[-1]["analyses"], [])

    def test_offsets_on_normalized_text(self):
        normalized = "مكتوب  ABC!"
        result = analyze_text(normalized)
        self.assertEqual([normalized[r["start"]:r["end"]] for r in result],
                         [r["token"] for r in result])

    def test_empty_and_type_validation(self):
        self.assertEqual(analyze_text(""), [])
        with self.assertRaises(TypeError):
            analyze_text(None)


if __name__ == "__main__":
    unittest.main()
