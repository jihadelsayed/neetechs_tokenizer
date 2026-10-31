import unittest
from unittest.mock import patch
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

    def test_single_root_not_mistaken_for_ambiguity(self):
        r = benchmark_cases([{"word": "كتبت", "root": "كتب"}])
        self.assertEqual(r["ambiguous_top_root_cases"], 0)

    def test_abstention_excluded_from_unique_rank_denominator(self):
        r = benchmark_cases([{"word": "مكتوب", "root": "كتب"},
                             {"word": "قاموا", "root": "قوم"}])
        self.assertEqual(r["uniquely_ranked_cases"], 1)
        self.assertEqual(r["abstained_cases"], 1)
        self.assertEqual(r["unambiguous_top_root_accuracy"], 1.0)

    def test_distinct_root_tie(self):
        shared = {"score": 0.9}
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": [
                       dict(shared, root="كتب"),
                       dict(shared, root="كبت")
                   ]}):
            r = benchmark_cases([{"word": "test", "root": "كبت"}])
        self.assertEqual(r["ambiguous_top_root_cases"], 1)
        self.assertEqual(r["uniquely_ranked_cases"], 0)
        self.assertIsNone(r["unambiguous_top_root_accuracy"])

    def test_multiple_accepted_roots(self):
        from unittest.mock import patch
        analyses = [{"root": "كتب", "score": 0.8}]
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": analyses}):
            result = benchmark_cases([{"word": "مثال", "roots": ["كتب", "كبت"]}])
        self.assertEqual(result["root_recall_at_any_candidate"], 1.0)
        self.assertEqual(result["top_one_root_accuracy"], 1.0)
        self.assertEqual(result["unambiguous_top_root_accuracy"], 1.0)
        self.assertEqual(result["uniquely_ranked_cases"], 1)

    def test_invalid_multiple_annotations(self):
        for case in (
            {"word": "مثال", "roots": []},
            {"word": "مثال", "roots": ["كتب", "كتب"]},
            {"word": "مثال", "root": "كتب", "roots": ["كتب"]},
            {"word": "مثال", "roots": ["كتب", 123]},
        ):
            with self.subTest(case=case), self.assertRaises(ValueError):
                benchmark_cases([case])

    def test_ties_use_max_score_not_first_position(self):
        analyses = [
            {"root": "كتب", "score": 0.4},
            {"root": "علم", "score": 0.9},
            {"root": "فتح", "score": 0.9},
        ]
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": analyses}):
            result = benchmark_cases([{"word": "example", "root": "علم"}])
        self.assertEqual(result["ambiguous_top_root_cases"], 1)
        self.assertEqual(result["uniquely_ranked_cases"], 0)

    def test_top_one_uses_highest_score_even_if_unsorted(self):
        analyses = [{"root": "كتب", "score": 0.2},
                    {"root": "علم", "score": 0.9}]
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": analyses}):
            result = benchmark_cases([{"word": "example", "root": "علم"}])
        self.assertEqual(result["top_one_correct"], 1)
        self.assertEqual(result["top_one_root_accuracy"], 1.0)
        self.assertEqual(result["unambiguous_top_root_accuracy"], 1.0)

    def test_top_one_is_invariant_to_input_order(self):
        analyses = [{"root": "علم", "score": 0.9},
                    {"root": "كتب", "score": 0.9}]
        outputs = []
        for ordering in (analyses, list(reversed(analyses))):
            with patch("neetechs_tokenizer.benchmark.word_analyzer",
                       return_value={"analyses": ordering}):
                outputs.append(benchmark_cases([{"word": "example", "root": "علم"}]))
        self.assertEqual(outputs[0]["top_one_correct"], outputs[1]["top_one_correct"])
        self.assertEqual(outputs[0]["ambiguous_top_root_cases"], 1)

    def test_tie_aware_metric_needs_all_tied_roots_accepted(self):
        analyses = [{"root": "كتب", "score": 0.9},
                    {"root": "كبت", "score": 0.9}]
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": analyses}):
            partial = benchmark_cases([{"word": "example", "root": "كتب"}])
            both = benchmark_cases([{"word": "example", "roots": ["كتب", "كبت"]}])
        self.assertEqual(partial["tie_aware_top_accuracy"], 0.0)
        self.assertEqual(both["tie_aware_top_accuracy"], 1.0)

    def test_diagnostic_error_categories(self):
        scenarios = {
            "ok": [{"root": "كتب", "score": 0.9}],
            "wrong": [{"root": "علم", "score": 0.9}, {"root": "كتب", "score": 0.2}],
            "missing": [{"root": "علم", "score": 0.9}],
            "tie": [{"root": "كتب", "score": 0.9}, {"root": "علم", "score": 0.9}],
            "none": [],
        }
        def analyzer(word):
            return {"analyses": scenarios[word]}
        with patch("neetechs_tokenizer.benchmark.word_analyzer", side_effect=analyzer):
            result = benchmark_cases([{"word": word, "root": "كتب"} for word in scenarios])
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["error_category_counts"], {
            "abstained": 1, "wrong_top_root": 2,
            "ambiguous_top_root": 1, "expected_root_missing": 1,
        })
        self.assertEqual(result["selective_coverage"], 3 / 5)
        self.assertEqual(result["selective_accuracy"], 1 / 3)
        self.assertEqual(result["case_results"][0]["error_categories"], [])
        self.assertEqual(result["case_results"][1]["error_categories"], ["wrong_top_root"])
        self.assertEqual(result["case_results"][2]["error_categories"],
                         ["wrong_top_root", "expected_root_missing"])
        self.assertEqual(result["case_results"][3]["error_categories"],
                         ["ambiguous_top_root"])
        self.assertEqual(result["case_results"][4]["error_categories"], ["abstained"])

    def test_all_abstain_has_no_selective_accuracy(self):
        with patch("neetechs_tokenizer.benchmark.word_analyzer",
                   return_value={"analyses": []}):
            result = benchmark_cases([{"word": "unknown", "root": "كتب"}])
        self.assertIsNone(result["selective_accuracy"])
        self.assertEqual(result["selective_coverage"], 0.0)

    def test_empty(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            benchmark_cases([])

    def test_bad_labels_rejected(self):
        with self.assertRaises(ValueError):
            benchmark_cases([{"word": "مكتوب"}])


if __name__ == "__main__":
    unittest.main()
