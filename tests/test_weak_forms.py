import unittest
from neetechs_tokenizer import wordAnalyzer, analyze_weak_verb


class WeakVerbTests(unittest.TestCase):
    def test_hollow_waw_root(self):
        for form in ("قال", "يقول", "قل"):
            with self.subTest(form=form):
                self.assertEqual(analyze_weak_verb(form)[0]["root"], "قول")

    def test_hollow_ya_root(self):
        for form in ("باع", "يبيع", "بع"):
            with self.subTest(form=form):
                self.assertEqual(analyze_weak_verb(form)[0]["root"], "بيع")

    def test_defective_waw_root(self):
        for form in ("دعا", "يدعو", "ادع"):
            with self.subTest(form=form):
                self.assertEqual(analyze_weak_verb(form)[0]["root"], "دعو")

    def test_ambiguity_in_first_second_person(self):
        readings = analyze_weak_verb("قلت")
        self.assertEqual(len(readings), 3)
        self.assertEqual({x["person"] for x in readings}, {1, 2})

    def test_integrated(self):
        self.assertTrue(any(a["root"] == "قول" and a.get("weak_root")
                            for a in wordAnalyzer("يقول")["analyses"]))

    def test_negative(self):
        self.assertEqual(analyze_weak_verb("قام"), [])
        self.assertEqual(analyze_weak_verb("ذهب"), [])

    def test_type_validation(self):
        with self.assertRaises(TypeError):
            analyze_weak_verb(None)


if __name__ == "__main__":
    unittest.main()
