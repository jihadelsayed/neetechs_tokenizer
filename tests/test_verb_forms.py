import unittest

from neetechs_tokenizer import analyze_imperfect, analyze_imperative, wordAnalyzer, tokenize


class VerbFormTests(unittest.TestCase):
    def test_imperfect_masculine(self):
        a = analyze_imperfect("يكتب")
        self.assertEqual(len(a), 1)
        self.assertEqual((a[0]["root"], a[0]["tense"], a[0]["person"]), ("كتب", "imperfect", 3))

    def test_imperfect_feminine_ambiguity(self):
        a = analyze_imperfect("تكتب")
        self.assertEqual(len(a), 2)
        self.assertEqual({(x["person"], x["gender"]) for x in a},
                         {(2, "masculine"), (3, "feminine")})

    def test_plurals(self):
        self.assertEqual(analyze_imperfect("نكتب")[0]["number"], "plural")
        self.assertEqual(analyze_imperfect("يكتبون")[0]["number"], "plural")
        self.assertEqual(analyze_imperfect("تكتبون")[0]["person"], 2)

    def test_dual_ambiguity(self):
        self.assertEqual(len(analyze_imperfect("تكتبان")), 2)

    def test_imperative(self):
        a = analyze_imperative("اكتب")
        self.assertEqual((a[0]["root"], a[0]["tense"]), ("كتب", "imperative"))
        self.assertEqual(analyze_imperative("افتح")[0]["root"], "فتح")

    def test_no_invented_forms(self):
        self.assertEqual(analyze_imperfect("يذهب"), [])
        self.assertEqual(analyze_imperative("اقرأ"), [])

    def test_main_api(self):
        self.assertTrue(any(a.get("tense") == "imperfect" for a in wordAnalyzer("يفتح")["analyses"]))
        self.assertEqual(tokenize("اكتب"), ["اكتب"])

    def test_invalid_types(self):
        with self.assertRaises(TypeError):
            analyze_imperfect(None)
        with self.assertRaises(TypeError):
            analyze_imperative(None)


if __name__ == "__main__":
    unittest.main()
