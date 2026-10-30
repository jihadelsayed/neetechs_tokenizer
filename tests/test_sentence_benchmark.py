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

    def test_uncached_results_are_independent(self):
        rows = uncached_analysis("مكتوب مكتوب")
        self.assertTrue(rows[0]["analyses"])
        root = rows[1]["analyses"][0]["root"]
        rows[0]["analyses"][0]["root"] = "changed"
        self.assertEqual(rows[1]["analyses"][0]["root"], root)

    def test_cache_reduces_morphology_calls(self):
        from unittest.mock import patch
        import neetechs_tokenizer.tokenizer as tokenizer_module
        import scripts.benchmark_sentence_cache as benchmark_module

        sentence = " ".join(["مكتوب", "الكاتب"] * 200)
        with patch.object(tokenizer_module, "word_analyzer",
                          wraps=tokenizer_module.word_analyzer) as cached_mock:
            cached = analyze_text(sentence)
        with patch.object(benchmark_module, "word_analyzer",
                          wraps=benchmark_module.word_analyzer) as uncached_mock:
            uncached = uncached_analysis(sentence)

        self.assertEqual(cached, uncached)
        self.assertEqual(cached_mock.call_count, 2)
        self.assertEqual(uncached_mock.call_count, 400)

    def test_reject_invalid_parameters(self):
        for repeats, iterations in ((0, 1), (1, 0), (-1, 2)):
            with self.subTest(repeats=repeats, iterations=iterations):
                with self.assertRaises(ValueError):
                    benchmark(repeats, iterations)
