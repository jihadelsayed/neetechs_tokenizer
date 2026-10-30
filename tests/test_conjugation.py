import unittest
from neetechs_tokenizer import word_analyzer, analyze_perfect, tokenize


class ConjugationTests(unittest.TestCase):
    def test_first_plural(self):
        result = analyze_perfect("كتبنا")
        self.assertEqual(len(result), 1)
        self.assertEqual((result[0]["root"], result[0]["person"], result[0]["number"]), ("كتب", 1, "plural"))

    def test_ambiguous_t_suffix(self):
        result = analyze_perfect("كتبت")
        self.assertEqual(len(result), 4)
        self.assertEqual({x["person"] for x in result}, {1, 2, 3})

    def test_form_x(self):
        self.assertEqual(analyze_perfect("استكتبتم")[0]["pattern"], "استفعل")

    def test_plural_form(self):
        self.assertEqual(analyze_perfect("كتبوا")[0]["number"], "plural")
        self.assertEqual(tokenize("كتبوا"), ["كتب", "وا"])

    def test_no_unsupported_guess(self):
        self.assertEqual(analyze_perfect("قاموا"), [])
        self.assertEqual(analyze_perfect("طالبات"), [])

    def test_integrated(self):
        result = word_analyzer("فتحتم")["analyses"]
        self.assertTrue(any(x.get("tense") == "perfect" and x["root"] == "فتح" for x in result))

    def test_preserve_lexical_ambiguity(self):
        result = word_analyzer("درس")["analyses"]
        self.assertTrue(any(x["part_of_speech"] == "noun" for x in result))
        self.assertTrue(any(x["part_of_speech"] == "verb" for x in result))


if __name__ == "__main__":
    unittest.main()
