"""Public API smoke contract for the v0.9.x library."""
import unittest

import neetechs_tokenizer as api


class PublicAPISmokeTests(unittest.TestCase):
    def test_public_exports_are_callable(self):
        for name in api.__all__:
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(api, name)))

    def test_surface_and_clitic_modes(self):
        self.assertEqual(api.tokenize("والكاتب!", split_clitics=False),
                         ["والكاتب", "!"])
        self.assertEqual(api.tokenize("والكاتب!"), ["و", "ال", "كاتب", "!"])

    def test_root_lookup_and_unknown_abstention(self):
        self.assertEqual(api.get_root("مكتوب"), "كتب")
        self.assertIsNone(api.get_root("كلمةغيرمعروفة"))
        self.assertEqual(api.wordAnalyzer("مكتوب"),
                         api.word_analyzer("مكتوب"))

    def test_sentence_records_have_stable_fields(self):
        result = api.analyze_text("مكتوب!", include_segments=True)
        self.assertEqual([item["token"] for item in result],
                         ["مكتوب", "!"])
        for item in result:
            self.assertTrue({"token", "start", "end", "analyses",
                             "segments"} <= item.keys())
            self.assertEqual("".join(item["segments"]), item["token"])

    def test_repeated_sentence_analyses_are_independent(self):
        result = api.analyze_text("مكتوب مكتوب")
        self.assertEqual(len(result), 2)
        self.assertIsNot(result[0]["analyses"], result[1]["analyses"])
        self.assertTrue(result[0]["analyses"])
        result[0]["analyses"][0]["root"] = "changed"
        self.assertEqual(result[1]["analyses"][0]["root"], "كتب")


if __name__ == "__main__":
    unittest.main()
