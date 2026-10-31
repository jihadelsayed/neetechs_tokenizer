"""Malformed reviewer roots must not silently become distinct labels."""
import unittest

from scripts.review_agreement import adjudicate
from scripts.adjudicate_reviews import resolve_reviews


class ReviewRootWhitespaceTests(unittest.TestCase):
    def test_reviewer_root_with_surrounding_space_rejected(self):
        a = [{"word": "كتب", "roots": ["كتب "]}]
        b = [{"word": "كتب", "roots": ["كتب"]}]
        with self.assertRaisesRegex(ValueError, "Invalid root annotation"):
            adjudicate(a, b)

    def test_adjudicator_root_with_surrounding_space_rejected(self):
        a = [{"word": "كتب", "roots": ["كتب"]}]
        b = [{"word": "كتب", "roots": ["درس"]}]
        decisions = [{"word": "كتب", "roots": [" كتب"],
                      "adjudicator": "third", "rationale": "test"}]
        with self.assertRaisesRegex(ValueError, "Invalid adjudicated roots"):
            resolve_reviews(a, b, decisions)


if __name__ == "__main__":
    unittest.main()
