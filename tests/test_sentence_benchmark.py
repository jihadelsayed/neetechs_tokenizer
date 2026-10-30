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
        from importlib import import_module
        tokenizer_module = import_module("neetechs_tokenizer.tokenizer")
        benchmark_module = import_module("scripts.benchmark_sentence_cache")

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

    def test_cache_is_scoped_to_single_analysis_call(self):
        from unittest.mock import patch
        from importlib import import_module

        tokenizer_module = import_module("neetechs_tokenizer.tokenizer")
        with patch.object(tokenizer_module, "word_analyzer",
                          wraps=tokenizer_module.word_analyzer) as mocked:
            first = analyze_text("مكتوب مكتوب")
            second = analyze_text("مكتوب مكتوب")

        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(first, second)
        self.assertIsNot(first[0]["analyses"], second[0]["analyses"])

    def test_distinct_workload_smoke(self):
        result = benchmark(repeats=2, iterations=2, workload="distinct")
        self.assertEqual(result["tokens_per_run"], 8)
        self.assertEqual(result["workload"], "distinct")

    def test_reject_unknown_workload(self):
        with self.assertRaises(ValueError):
            benchmark(repeats=1, iterations=1, workload="invalid")

    def test_reject_invalid_parameters(self):
        for repeats, iterations in ((0, 1), (1, 0), (-1, 2)):
            with self.subTest(repeats=repeats, iterations=iterations):
                with self.assertRaises(ValueError):
                    benchmark(repeats, iterations)
