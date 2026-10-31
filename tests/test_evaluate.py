import unittest
from neetechs_tokenizer.evaluate import evaluate_cases, load_cases


class QualityGateTests(unittest.TestCase):
    def test_dataset(self):
        self.assertGreaterEqual(len(load_cases()), 20)

    def test_false_positive_detected(self):
        result = evaluate_cases([{"word": "مكتوب", "unknown": True}])
        self.assertFalse(result["passed"])
        self.assertEqual(result["failures"][0]["reason"], "false_positive")

    def test_missing_root_detected(self):
        result = evaluate_cases([{"word": "مكتوب", "root": "علم"}])
        self.assertFalse(result["passed"])
        self.assertEqual(result["correct_positive"], 0)

    def test_correct_positive_and_negative(self):
        result = evaluate_cases([
            {"word": "مكتوب", "root": "كتب", "pattern": "مفعول"},
            {"word": "والورد", "unknown": True},
        ])
        self.assertTrue(result["passed"], result)
        self.assertEqual((result["correct_positive"], result["correct_negative"]), (1, 1))

    def test_segmentation_failure(self):
        result = evaluate_cases([
            {"word": "مكتوب", "root": "كتب", "tokens": ["incorrect"]}
        ])
        self.assertFalse(result["passed"])
        self.assertEqual(result["failures"][0]["reason"], "incorrect_segmentation")

    def test_supported_and_unsupported_metrics(self):
        result = evaluate_cases([
            {"word": "مكتوب", "root": "كتب"},
            {"word": "قاموا", "unknown": True},
        ])
        self.assertEqual(result["expected_unsupported"], 1)
        self.assertEqual(result["rejected_unsupported"], 1)
        self.assertEqual(result["supported_case_coverage"], 1.0)
        self.assertIn("not true negatives", result["note"])

    def test_empty_dataset(self):
        with self.assertRaisesRegex(ValueError, "at least one case"):
            evaluate_cases([])


if __name__ == "__main__":
    unittest.main()
