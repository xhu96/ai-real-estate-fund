from __future__ import annotations

import unittest

from ai_real_estate_fund.finance import annual_debt_service, remaining_loan_balance, underwrite_property
from ai_real_estate_fund.models import PropertyInput


class FinanceTests(unittest.TestCase):
    def test_annual_debt_service_zero_loan(self) -> None:
        self.assertEqual(annual_debt_service(0, 0.07, 30), 0.0)

    def test_annual_debt_service_positive(self) -> None:
        debt_service = annual_debt_service(100_000, 0.06, 30)
        self.assertGreater(debt_service, 7000)
        self.assertLess(debt_service, 8000)

    def test_remaining_balance_declines(self) -> None:
        start = remaining_loan_balance(100_000, 0.06, 30, 0)
        year_five = remaining_loan_balance(100_000, 0.06, 30, 5)
        self.assertLess(year_five, start)

    def test_underwrite_property_metrics(self) -> None:
        prop = PropertyInput(
            name="Test",
            address="123 Test",
            market="Testville",
            purchase_price=200_000,
            estimated_arv=220_000,
            monthly_rent=2400,
            vacancy_rate=0.05,
            property_taxes_annual=3000,
            insurance_annual=1500,
            repairs_annual=2000,
            capex_annual=1500,
            acquisition_costs=5000,
            rehab_budget=5000,
            loan_amount=150_000,
            annual_interest_rate=0.07,
        )
        metrics = underwrite_property(prop)
        self.assertGreater(metrics.noi, 0)
        self.assertGreater(metrics.cap_rate, 0)
        self.assertGreater(metrics.cash_invested, 0)


if __name__ == "__main__":
    unittest.main()
