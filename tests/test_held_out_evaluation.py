import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_held_out_evaluation import run_evaluation


class HeldOutEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.dataset = root / "dataset.json"
        self.manifest = root / "manifest.json"
        self.dataset.write_text(json.dumps({
            "schema_version": 1,
            "metadata": {"status": "adjudicated_not_independently_verified"},
            "cases": [{"word": "مكتوب", "roots": ["كتب"]}],
            "audit": {"agreement_rate": 1.0, "adjudications": []}
        }), encoding="utf-8")
        self.manifest.write_text(json.dumps({
            "frozen_commit": "a" * 40,
            "dataset_sha256": hashlib.sha256(self.dataset.read_bytes()).hexdigest(),
            "source": "reviewer-provided", "license": "CC-BY-4.0",
            "language_variety": "MSA", "collection_date": "2026-10-30",
            "reviewer_a": "a", "reviewer_b": "b", "adjudicator": "c",
            "annotation_guide": "v1", "blind_review_confirmed": True,
            "held_out_from_tuning_confirmed": True, "frozen_code_verified": True
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_report_includes_frozen_versions_not_accuracy_approval(self):
        result = run_evaluation(self.dataset, self.manifest, revision="a" * 40)
        self.assertEqual(result["dataset_sha256"],
                         hashlib.sha256(self.dataset.read_bytes()).hexdigest())
        self.assertEqual(result["frozen_commit"], "a" * 40)
        self.assertEqual(result["metrics"]["total"], 1)
        self.assertFalse(result["independent_accuracy_verified"])

    def test_rejects_different_source_revision(self):
        with self.assertRaisesRegex(ValueError, "differs"):
            run_evaluation(self.dataset, self.manifest, revision="b" * 40)

    def test_rejects_modified_dataset_before_scoring(self):
        self.dataset.write_text(self.dataset.read_text() + " ", encoding="utf-8")
        with patch("scripts.run_held_out_evaluation.benchmark_cases") as benchmark:
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run_evaluation(self.dataset, self.manifest, revision="a" * 40)
            benchmark.assert_not_called()


if __name__ == "__main__":
    unittest.main()
