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

    def test_article_and_possessive_incompatible(self):
        for word in ("الكاتبهم", "والكاتبها", "بالكتابهم"):
            with self.subTest(word=word):
                self.assertEqual(wordAnalyzer(word)["analyses"], [])
                self.assertEqual(tokenize(word), [word])

    def test_article_possessive_candidates_rejected_early(self):
        for word in ("الكاتبهم", "والكاتبها", "بالكتابه",
                     "وبالكتابهم", "وكالمفتاحها"):
            with self.subTest(word=word):
                self.assertFalse(any(
                    "ال" in candidate.prefixes and
                    any(label.startswith("possessive-or-object:")
                        for label in candidate.labels)
                    for candidate in priority_identifier(word)
                ))

    def test_bare_noun_possessive_candidate_retained(self):
        self.assertTrue(any(
            candidate.stem == "كتاب" and candidate.suffixes == ("ه",)
            for candidate in priority_identifier("كتابه")
        ))

    def test_possessive_without_article_still_supported(self):
        self.assertTrue(any(
            a["part_of_speech"] == "noun"
            for a in wordAnalyzer("كتابهم")["analyses"]
        ))

    def test_compound_preposition_article(self):
        for word, expected in (
            ("وبالكتاب", ["و", "ب", "ال", "كتاب"]),
            ("فبالكتاب", ["ف", "ب", "ال", "كتاب"]),
            ("وكالمفتاح", ["و", "ك", "ال", "مفتاح"]),
            ("فكالمفتاح", ["ف", "ك", "ال", "مفتاح"]),
        ):
            with self.subTest(word=word):
                self.assertEqual(tokenize(word), expected)
                self.assertEqual("".join(expected), word)

    def test_third_person_singular_pronoun(self):
        analysis = wordAnalyzer("كتابه")["analyses"]
        self.assertTrue(any(a["root"] == "كتب"
                            and a["part_of_speech"] == "noun"
                            and [s["surface"] for s in a["suffixes"]] == ["ه"]
                            for a in analysis))
        self.assertEqual(tokenize("كتابه"), ["كتاب", "ه"])

    def test_compound_article_possessive_stays_rejected(self):
        for word in ("وبالكتابهم", "فبالكتابه", "وكالمفتاحها"):
            with self.subTest(word=word):
                self.assertEqual(wordAnalyzer(word)["analyses"], [])
                self.assertEqual(tokenize(word), [word])

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
