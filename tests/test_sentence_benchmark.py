import unittest
from scripts.benchmark_sentence_cache import benchmark, uncached_analysis
from neetechs_tokenizer import analyze_text


class SentenceBenchmarkTests(unittest.TestCase):
    def test_small_benchmark_smoke(self):
        result = benchmark(repeats=1, iterations=2)
        self.assertEqual(result["tokens_per_run"], 4)
        self.assertEqual(result["iterations"], 2)
        self.assertGreaterEqual(result["median_seconds"], 0)
        self.assertGreaterEqual(result["uncached_median_seconds"], 0)

    def test_baseline_matches_cached_analysis(self):
        sentence = "مكتوب الكاتب! مكتوب"
        self.assertEqual(uncached_analysis(sentence), analyze_text(sentence))

    def test_reject_invalid_parameters(self):
        for repeats, iterations in ((0, 1), (1, 0), (-1, 2)):
            with self.subTest(repeats=repeats, iterations=iterations):
                with self.assertRaises(ValueError):
                    benchmark(repeats, iterations)
