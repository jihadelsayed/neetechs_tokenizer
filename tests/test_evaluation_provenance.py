import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_evaluation_provenance import verify_provenance


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.dataset = root / "evaluation.json"
        self.manifest = root / "manifest.json"
        self.dataset.write_text(json.dumps({
            "schema_version": 1,
            "metadata": {"status": "adjudicated_not_independently_verified"},
            "cases": [{"word": "كتب", "roots": ["كتب"]}],
            "audit": {"agreement_rate": 1.0, "adjudications": []}
        }), encoding="utf-8")
        self.metadata = {
            "frozen_commit": "a" * 40,
            "dataset_sha256": hashlib.sha256(self.dataset.read_bytes()).hexdigest(),
            "source": "Reviewer-provided holdout", "license": "CC-BY-4.0",
            "language_variety": "Modern Standard Arabic",
            "collection_date": "2026-10-30",
            "reviewer_a": "a", "reviewer_b": "b", "adjudicator": "c",
            "annotation_guide": "v1", "blind_review_confirmed": True,
            "held_out_from_tuning_confirmed": True,
            "frozen_code_verified": True
        }

    def tearDown(self):
        self.temp.cleanup()

    def check(self):
        self.manifest.write_text(json.dumps(self.metadata), encoding="utf-8")
        return verify_provenance(self.dataset, self.manifest)

    def test_valid_declarations_do_not_establish_independent_accuracy(self):
        report = self.check()
        self.assertTrue(report["manifest_valid"])
        self.assertFalse(report["independent_accuracy_verified"])

    def test_modified_dataset_rejected(self):
        self.dataset.write_text(self.dataset.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.check()

    def test_missing_provenance_rejected(self):
        del self.metadata["license"]
        with self.assertRaisesRegex(ValueError, "license"):
            self.check()

    def test_unconfirmed_blind_review_rejected(self):
        self.metadata["blind_review_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "Blind review"):
            self.check()

    def test_reviewer_identity_collision_rejected(self):
        self.metadata["adjudicator"] = "a"
        with self.assertRaisesRegex(ValueError, "distinct"):
            self.check()


if __name__ == "__main__":
    unittest.main()
