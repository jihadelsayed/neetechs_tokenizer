"""Synthetic end-to-end pipeline exercise; never a linguistic accuracy benchmark."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.review_agreement import adjudicate
from scripts.adjudicate_reviews import resolve_reviews
from scripts.run_held_out_evaluation import run_evaluation


class SyntheticEvaluationPipelineTests(unittest.TestCase):
    def test_blind_review_through_frozen_benchmark(self):
        # Artificial annotations exercise the software flow, not linguistic truth.
        reviewer_a = [
            {"word": "مكتوب", "roots": ["كتب"]},
            {"word": "غامض", "status": "uncertain", "reason": "Missing context"},
            {"word": "فتح", "roots": ["فتح"]},
        ]
        reviewer_b = [
            {"word": "فتح", "roots": ["كتب"]},
            {"word": "مكتوب", "roots": ["كتب"]},
            {"word": "غامض", "status": "uncertain", "reason": "Ambiguous"},
        ]
        agreement = adjudicate(reviewer_a, reviewer_b)
        self.assertEqual(agreement["total"], 3)
        self.assertEqual(len(agreement["disagreements"]), 1)
        review = resolve_reviews(reviewer_a, reviewer_b, [
            {"word": "فتح", "roots": ["فتح"], "adjudicator": "synthetic_c",
             "rationale": "Synthetic exercise only"}
        ])
        self.assertEqual(review["audit"]["total_reviewed"], 3)
        self.assertEqual(review["audit"]["included_cases"], 2)
        self.assertEqual(review["audit"]["excluded_cases"], 1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "synthetic-adjudicated.json"
            manifest = root / "synthetic-manifest.json"
            dataset.write_text(json.dumps(review, ensure_ascii=False),
                               encoding="utf-8")
            metadata = {
                "frozen_commit": "a" * 40,
                "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
                "source": "SYNTHETIC TEST FIXTURE - NOT INDEPENDENT",
                "license": "Internal test fixture",
                "language_variety": "MSA fixture",
                "collection_date": "2026-10-30",
                "reviewer_a": "synthetic_a", "reviewer_b": "synthetic_b",
                "adjudicator": "synthetic_c", "annotation_guide": "synthetic",
                "blind_review_confirmed": True,
                "held_out_from_tuning_confirmed": True,
                "frozen_code_verified": True,
            }
            manifest.write_text(json.dumps(metadata), encoding="utf-8")
            with patch("scripts.run_held_out_evaluation.benchmark_cases",
                       return_value={"total": 2, "coverage": 0.5,
                                     "top_one_correct": 1}) as benchmark:
                result = run_evaluation(dataset, manifest, revision="a" * 40)
                benchmark.assert_called_once_with(review["cases"])

        self.assertFalse(result["independent_accuracy_verified"])
        self.assertEqual(result["review_metrics"]["total_reviewed"], 3)
        self.assertEqual(result["review_metrics"]["excluded_cases"], 1)
        self.assertAlmostEqual(
            result["review_metrics"]["analyzer_coverage_of_all_reviewed"], 1/3)
        self.assertAlmostEqual(
            result["review_metrics"]["top_one_correct_of_all_reviewed"], 1/3)


if __name__ == "__main__":
    unittest.main()
