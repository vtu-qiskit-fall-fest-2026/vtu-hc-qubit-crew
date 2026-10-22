
import unittest

from src.explanations import explain_risk


class TestRiskExplanations(unittest.TestCase):
    def test_no_warning_signs(self):
        opportunity = {
            "upfront_fee": 0,
            "unverified_sender": 0,
            "unrealistic_pay": 0,
            "pressure_tactics": 0,
            "missing_details": 0,
        }

        result = explain_risk(opportunity)

        self.assertEqual(result["warning_count"], 0)
        self.assertEqual(result["warnings"], [])

    def test_multiple_warning_signs(self):
        opportunity = {
            "upfront_fee": 1,
            "unverified_sender": 1,
            "unrealistic_pay": 0,
            "pressure_tactics": 1,
            "missing_details": 1,
        }

        result = explain_risk(opportunity)

        self.assertEqual(result["warning_count"], 4)
        self.assertEqual(len(result["warnings"]), 4)

    def test_invalid_feature_value(self):
        opportunity = {
            "upfront_fee": 2,
        }

        with self.assertRaises(ValueError):
            explain_risk(opportunity)


if __name__ == "__main__":
    unittest.main()
