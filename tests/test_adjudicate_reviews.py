import unittest
from scripts.adjudicate_reviews import resolve_reviews


class AdjudicationTests(unittest.TestCase):
    def test_agreed_cases_need_no_adjudication(self):
        rows = [{"word": "كتب", "roots": ["كتب"]}]
        report = resolve_reviews(rows, list(rows), [])
        self.assertEqual(report["cases"], rows)
        self.assertEqual(report["audit"]["adjudications"], [])
        self.assertNotEqual(report["metadata"]["status"], "independently_verified")

    def test_third_reviewer_resolves_disagreement_with_audit(self):
        a = [{"word": "كتب", "roots": ["كتب"]}]
        b = [{"word": "كتب", "roots": ["كبت"]}]
        decision = [{"word": "كتب", "roots": ["كتب"], "adjudicator": "reviewer_c",
                     "rationale": "Reviewed root in context"}]
        report = resolve_reviews(a, b, decision)
        self.assertEqual(report["cases"], [{"word": "كتب", "roots": ["كتب"]}])
        self.assertEqual(report["audit"]["adjudications"][0]["reviewer_b"], ["كبت"])

    def test_unresolved_conflicts_fail_closed(self):
        a = [{"word": "كتب", "roots": ["كتب"]}]
        b = [{"word": "كتب", "roots": ["كبت"]}]
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            resolve_reviews(a, b, [])

    def test_no_decisions_for_agreed_words(self):
        rows = [{"word": "كتب", "roots": ["كتب"]}]
        decision = [{"word": "كتب", "roots": ["كتب"], "adjudicator": "c",
                     "rationale": "not needed"}]
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            resolve_reviews(rows, rows, decision)

    def test_missing_rationale_rejected(self):
        a = [{"word": "كتب", "roots": ["كتب"]}]
        b = [{"word": "كتب", "roots": ["كبت"]}]
        with self.assertRaisesRegex(ValueError, "rationale"):
            resolve_reviews(a, b, [{"word": "كتب", "roots": ["كتب"],
                                     "adjudicator": "c"}])


if __name__ == "__main__":
    unittest.main()
