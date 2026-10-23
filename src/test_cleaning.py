import math
import unittest

from build_case_study import clean_dataset, parse_float


class CleaningTests(unittest.TestCase):
    def test_valid_zero_money_is_not_replaced_with_an_estimate(self):
        row = clean_dataset([{
            "ticket_id": "ZERO", "revenue_value": "0", "cost_estimate": "0",
            "satisfaction_score": "0",
        }])[0]
        self.assertEqual(row["revenue_value"], 0)
        self.assertEqual(row["cost_estimate"], 0)
        self.assertEqual(row["estimated_margin"], 0)
        self.assertEqual(row["satisfaction_score"], 1)

    def test_zero_cost_keeps_the_full_revenue_as_margin(self):
        row = clean_dataset([{
            "ticket_id": "NO_COST", "revenue_value": "100", "cost_estimate": "0",
        }])[0]
        self.assertEqual(row["cost_estimate"], 0)
        self.assertEqual(row["estimated_margin"], 100)

    def test_missing_money_still_receives_defaults(self):
        row = clean_dataset([{"ticket_id": "MISSING"}])[0]
        self.assertEqual(row["revenue_value"], 250)
        self.assertEqual(row["cost_estimate"], 87.5)
        self.assertEqual(row["satisfaction_score"], 3.8)

    def test_only_finite_nonnegative_numbers_are_accepted(self):
        for value in ["inf", "-inf", "NaN", "-1", "", "bad"]:
            with self.subTest(value=value):
                self.assertIsNone(parse_float(value))
        self.assertEqual(parse_float("$ 1,234.50"), 1234.5)
        self.assertTrue(math.isfinite(parse_float("0")))


if __name__ == "__main__":
    unittest.main()
