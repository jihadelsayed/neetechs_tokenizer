import unittest
from scripts.review_agreement import adjudicate


class ReviewAgreementTests(unittest.TestCase):
    def test_full_agreement_is_not_publication_approval(self):
        a = [{"word": "كتب", "roots": ["كتب"]}]
        result = adjudicate(a, list(a))
        self.assertEqual(result["agreement_rate"], 1.0)
        self.assertEqual(result["agreed_cases"], a)
        self.assertFalse(result["publishable_accuracy"])

    def test_disagreement_is_preserved_not_resolved(self):
        a = [{"word": "مثال", "roots": ["كتب"]}]
        b = [{"word": "مثال", "roots": ["كبت"]}]
        result = adjudicate(a, b)
        self.assertEqual(result["agreed"], 0)
        self.assertEqual(len(result["disagreements"]), 1)
        self.assertEqual(result["agreed_cases"], [])

    def test_order_does_not_change_agreement(self):
        a = [{"word": "كتب", "roots": ["كتب"]}, {"word": "فتح", "roots": ["فتح"]}]
        b = list(reversed(a))
        self.assertEqual(adjudicate(a, b)["agreement_rate"], 1.0)

    def test_rejects_mismatched_or_duplicate_reviews(self):
        for a, b in [
            ([{"word": "كتب", "roots": ["كتب"]}], []),
            ([{"word": "كتب", "roots": ["كتب"]}] * 2,
             [{"word": "كتب", "roots": ["كتب"]}]),
            ([{"word": "كتب", "roots": []}],
             [{"word": "كتب", "roots": ["كتب"]}]),
        ]:
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                adjudicate(a, b)


if __name__ == "__main__":
    unittest.main()
