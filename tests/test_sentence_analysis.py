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

    def test_original_offsets_with_diacritics_and_spaces(self):
        text = "  كَتَبَ  ABC!"
        rows = analyze_text(text, include_original_offsets=True)
        self.assertEqual([text[r["original_start"]:r["original_end"]] for r in rows],
                         ["كَتَبَ", "ABC", "!"])
        self.assertEqual([r["token"] for r in rows], ["كتب", "ABC", "!"])

    def test_normalized_offsets_unchanged(self):
        rows = analyze_text("  كَتَبَ!", include_original_offsets=True)
        self.assertEqual((rows[0]["start"], rows[0]["end"]), (0, 3))
        self.assertEqual((rows[0]["original_start"], rows[0]["original_end"]), (2, 8))

    def test_lam_alef_compatibility_ligature_offsets(self):
        text = "ﻻ!"
        rows = analyze_text(text, include_original_offsets=True)
        self.assertEqual([row["token"] for row in rows], ["لا", "!"])
        self.assertEqual((rows[0]["original_start"], rows[0]["original_end"]), (0, 1))
        self.assertEqual(text[rows[0]["original_start"]:rows[0]["original_end"]], "ﻻ")

    def test_tatweel_and_diacritics_offsets(self):
        text = "كـِتاب!"
        rows = analyze_text(text, include_original_offsets=True)
        self.assertEqual(rows[0]["token"], "كتاب")
        self.assertEqual(text[rows[0]["original_start"]:rows[0]["original_end"]], "كـِتاب")

    def test_empty_and_type_validation(self):
        self.assertEqual(analyze_text(""), [])
        with self.assertRaises(TypeError):
            analyze_text(None)


if __name__ == "__main__":
    unittest.main()
