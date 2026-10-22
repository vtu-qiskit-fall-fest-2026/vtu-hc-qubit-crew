
import unittest

from src.risk_assessment import assess_opportunity


class TestRiskAssessment(unittest.TestCase):
    def test_multiple_warning_signs(self):
        opportunity = {
            "upfront_fee": 1,
            "unverified_sender": 1,
            "unrealistic_pay": 0,
            "pressure_tactics": 1,
            "missing_details": 1,
        }

        result = assess_opportunity(opportunity)

        self.assertEqual(result["warning_count"], 4)
        self.assertEqual(result["assessment"], "Multiple warning signs")
        self.assertEqual(len(result["warnings"]), 4)

    def test_no_warning_signs(self):
        opportunity = {
            "upfront_fee": 0,
            "unverified_sender": 0,
            "unrealistic_pay": 0,
            "pressure_tactics": 0,
            "missing_details": 0,
        }

        result = assess_opportunity(opportunity)

        self.assertEqual(result["warning_count"], 0)
        self.assertEqual(result["warnings"], [])

    def test_missing_indicator_raises_error(self):
        opportunity = {
            "upfront_fee": 1,
        }

        with self.assertRaises(ValueError):
            assess_opportunity(opportunity)


if __name__ == "__main__":
    unittest.main()
