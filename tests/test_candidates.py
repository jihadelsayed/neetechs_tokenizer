import unittest

from neetechs_tokenizer import priority_identifier, priorityIdentifier, tokenize, wordAnalyzer


class CandidateTests(unittest.TestCase):
    def test_compound_article(self):
        candidates = priority_identifier("والكاتب")
        self.assertTrue(any(c.stem == "كاتب" and c.prefixes == ("و", "ال")
                            for c in candidates))
        self.assertEqual(tokenize("والكاتب"), ["و", "ال", "كاتب"])

    def test_pronouns(self):
        result = wordAnalyzer("استكتبوهم")["analyses"]
        self.assertTrue(any(a["root"] == "كتب"
                            and [s["surface"] for s in a["suffixes"]] == ["و", "هم"]
                            for a in result))

    def test_full_surface_reversible(self):
        for word in ("والمفتاح", "استكتبوهم", "بالكتاب", "كتبوا", "درس"):
            for c in priority_identifier(word):
                self.assertEqual("".join(c.prefixes) + c.stem
                                 + "".join(c.suffixes), word)

    def test_noun_article_verb_rejected(self):
        self.assertFalse(any(a["part_of_speech"] == "verb"
                             for a in wordAnalyzer("الكتب")["analyses"]))

    def test_future_false_positive_rejected(self):
        self.assertEqual(wordAnalyzer("سكتب")["analyses"], [])

    def test_unknowns_preserved(self):
        self.assertEqual(tokenize("وليد والورد"), ["وليد", "والورد"])

    def test_no_empty_stems(self):
        self.assertFalse(any(c.stem == "" for c in priority_identifier("و")))

    def test_compat_alias(self):
        self.assertEqual(priorityIdentifier("والكاتب"), priority_identifier("والكاتب"))

    def test_priority(self):
        c = priority_identifier("والكاتب")
        self.assertTrue(c)
        self.assertEqual(c[0].prefixes, ("و", "ال"))


if __name__ == "__main__":
    unittest.main()
