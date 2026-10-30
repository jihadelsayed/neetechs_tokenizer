"""Golden regression tests: small manually specified surface-level checks."""
import json
import unittest
from importlib.resources import files
from neetechs_tokenizer import tokenize, wordAnalyzer


class GoldenCorpusTests(unittest.TestCase):
    def test_golden_cases(self):
        path = files("neetechs_tokenizer").joinpath("data/regression.json")
        with path.open(encoding="utf-8") as f:
            vectors = json.load(f)["cases"]
        self.assertGreaterEqual(len(vectors), 20)
        for case in vectors:
            with self.subTest(word=case["word"]):
                analyses = wordAnalyzer(case["word"])["analyses"]
                if case.get("unknown"):
                    self.assertEqual(analyses, [])
                else:
                    matching = [
                        a for a in analyses
                        if a["root"] == case["root"]
                        and ("pattern" not in case or a["pattern"] == case["pattern"])
                        and ("tense" not in case or a.get("tense") == case["tense"])
                    ]
                    self.assertTrue(matching, (case["word"], analyses))
                if "tokens" in case:
                    self.assertEqual(tokenize(case["word"]), case["tokens"])

    def test_ambiguity_preserved(self):
        readings = wordAnalyzer("تكتب")["analyses"]
        self.assertGreaterEqual(len([a for a in readings if a.get("tense") == "imperfect"]), 2)

    def test_no_exact_duplicate_results(self):
        for word in ("كتب", "درس", "كتبت", "الكاتب", "استكتبوهم"):
            a = wordAnalyzer(word)["analyses"]
            keys = [(
                x["root"], x["pattern"], x["stem"], x["part_of_speech"],
                tuple(x["prefixes"]), tuple((s["surface"], s["function"]) for s in x["suffixes"]),
                x.get("tense"), x.get("person"), x.get("number"), x.get("gender")
            ) for x in a]
            self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
