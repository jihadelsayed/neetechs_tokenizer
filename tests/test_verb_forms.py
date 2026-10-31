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

    def test_reviewed_imperative_person_number_gender(self):
        forms = (
            ("اكتبي", "كتب", "singular", "feminine"),
            ("اكتبا", "كتب", "dual", None),
            ("اكتبوا", "كتب", "plural", "masculine"),
            ("افتحي", "فتح", "singular", "feminine"),
            ("افتحا", "فتح", "dual", None),
            ("افتحوا", "فتح", "plural", "masculine"),
        )
        for surface, root, number, gender in forms:
            with self.subTest(surface=surface):
                analyses = analyze_imperative(surface)
                self.assertEqual(len(analyses), 1)
                self.assertEqual((analyses[0]["root"], analyses[0]["person"],
                                  analyses[0]["number"], analyses[0]["gender"]),
                                 (root, 2, number, gender))
                self.assertTrue(any(a.get("tense") == "imperative"
                                    and a["root"] == root
                                    for a in wordAnalyzer(surface)["analyses"]))

    def test_unsupported_imperative_is_not_fabricated(self):
        self.assertEqual(analyze_imperative("اغسلوا"), [])

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
