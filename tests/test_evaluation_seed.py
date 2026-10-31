"""Keep the evaluation seed separate from training/regression fixtures."""
import json
import unittest
from importlib.resources import files
from pathlib import Path

from neetechs_tokenizer.benchmark import benchmark_cases


ROOT = Path(__file__).resolve().parents[1]


class EvaluationSeedTests(unittest.TestCase):
    def test_seed_is_well_formed_and_unreviewed(self):
        seed = json.loads((ROOT / "data/evaluation_seed.json").read_text(encoding="utf-8"))
        self.assertEqual(seed["schema_version"], 1)
        self.assertEqual(seed["metadata"]["status"], "draft_unreviewed")
        self.assertGreaterEqual(len(seed["cases"]), 20)
        words = [c["word"] for c in seed["cases"]]
        self.assertEqual(len(words), len(set(words)))
        for case in seed["cases"]:
            self.assertTrue(case["word"].strip())
            self.assertTrue(case["roots"])
            self.assertTrue(all(isinstance(root, str) and root.strip()
                                for root in case["roots"]))

    def test_no_regression_case_overlap(self):
        seed = json.loads((ROOT / "data/evaluation_seed.json").read_text(encoding="utf-8"))
        with files("neetechs_tokenizer").joinpath("data/regression.json").open(encoding="utf-8") as fh:
            regression = json.load(fh)
        self.assertFalse({c["word"] for c in seed["cases"]} &
                         {c["word"] for c in regression["cases"]})

    def test_benchmark_metrics_are_computable(self):
        seed = json.loads((ROOT / "data/evaluation_seed.json").read_text(encoding="utf-8"))
        result = benchmark_cases(seed["cases"])
        self.assertEqual(result["total"], len(seed["cases"]))
        self.assertIn("coverage", result)
        self.assertIn("top_one_root_accuracy", result)


if __name__ == "__main__":
    unittest.main()
