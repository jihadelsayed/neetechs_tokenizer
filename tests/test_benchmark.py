import unittest
from neetechs_tokenizer.benchmark import benchmark_cases


class BenchmarkTests(unittest.TestCase):
    def test_known_and_out_of_lexicon(self):
        r = benchmark_cases([{"word": "مكتوب", "root": "كتب"},
                             {"word": "قاموا", "root": "قوم"}])
        self.assertEqual(r["total"], 2)
        self.assertEqual(r["root_recall_at_any_candidate"], 0.5)
        self.assertEqual(r["coverage"], 0.5)
        self.assertEqual(r["top_one_root_accuracy"], 0.5)

    def test_top_one_metrics(self):
        r = benchmark_cases([{"word": "مكتوب", "root": "كتب"}])
        self.assertEqual(r["top_one_correct"], 1)
        self.assertEqual(r["top_one_errors"], 0)
        self.assertEqual(r["top_one_root_accuracy"], 1.0)

    def test_empty(self):
        self.assertIsNone(benchmark_cases([])["coverage"])

    def test_bad_labels_rejected(self):
        with self.assertRaises(ValueError):
            benchmark_cases([{"word": "مكتوب"}])


if __name__ == "__main__":
    unittest.main()
