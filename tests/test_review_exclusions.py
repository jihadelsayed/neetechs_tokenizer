import unittest
from scripts.review_agreement import adjudicate
from scripts.adjudicate_reviews import resolve_reviews


class ExclusionWorkflowTests(unittest.TestCase):
    def test_agreed_exclusions_not_scored(self):
        a = [{"word": "غامض", "status": "uncertain", "reason": "No context"},
             {"word": "كتب", "roots": ["كتب"]}]
        b = [{"word": "كتب", "roots": ["كتب"]},
             {"word": "غامض", "status": "uncertain", "reason": "Ambiguous"}]
        comparison = adjudicate(a, b)
        self.assertEqual(comparison["agreed"], 2)
        self.assertEqual(len(comparison["agreed_exclusions"]), 1)
        report = resolve_reviews(a, b, [])
        self.assertEqual(report["cases"], [{"word": "كتب", "roots": ["كتب"]}])
        self.assertEqual(report["audit"]["total_reviewed"], 2)
        self.assertEqual(report["audit"]["excluded_cases"], 1)

    def test_status_conflict_requires_adjudication(self):
        a = [{"word": "كتب", "status": "out_of_scope", "reason": "Test reason"}]
        b = [{"word": "كتب", "roots": ["كتب"]}]
        self.assertEqual(len(adjudicate(a, b)["disagreements"]), 1)
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            resolve_reviews(a, b, [])
        resolution = [{"word": "كتب", "status": "uncertain",
                       "rationale": "Context missing", "adjudicator": "third"}]
        output = resolve_reviews(a, b, resolution)
        self.assertEqual(output["cases"], [])
        self.assertEqual(output["exclusions"][0]["status"], "uncertain")

    def test_exclusions_require_reason_and_no_roots(self):
        for row in (
            {"word": "كتب", "status": "uncertain"},
            {"word": "كتب", "status": "out_of_scope", "reason": "x", "roots": ["كتب"]},
            {"word": "كتب", "status": "unknown", "reason": "x"},
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                adjudicate([row], [row])


if __name__ == "__main__":
    unittest.main()
