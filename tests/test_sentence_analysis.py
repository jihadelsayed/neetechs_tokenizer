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

    def test_optional_segments_match_tokenizer(self):
        from neetechs_tokenizer import tokenize
        text = "والكاتب بالكتاب!"
        result = analyze_text(text, include_segments=True)
        self.assertEqual([piece for item in result for piece in item["segments"]],
                         tokenize(text))
        self.assertTrue(all("".join(item["segments"]) == item["token"]
                            for item in result))

    def test_default_shape_unchanged(self):
        self.assertTrue(all("segments" not in item for item in analyze_text("مكتوب!")))

    def test_empty_and_type_validation(self):
        self.assertEqual(analyze_text(""), [])
        with self.assertRaises(TypeError):
            analyze_text(None)


if __name__ == "__main__":
    unittest.main()
