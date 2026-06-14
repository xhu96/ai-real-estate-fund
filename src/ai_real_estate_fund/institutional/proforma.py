from __future__ import annotations

from ..finance import annual_debt_service, remaining_loan_balance
from ..models import PropertyInput, UnderwritingMetrics
from .models import OperatingPlanYear


def build_operating_plan(prop: PropertyInput, base_metrics: UnderwritingMetrics, years: int | None = None) -> list[OperatingPlanYear]:
    horizon = years or prop.holding_period_years
    plan: list[OperatingPlanYear] = []
    gross_income = base_metrics.gross_potential_income
    non_management_expenses = (
        prop.property_taxes_annual
        + prop.insurance_annual
        + prop.repairs_annual
        + prop.utilities_annual
        + prop.hoa_annual
        + prop.capex_annual
    )
    debt_service = annual_debt_service(prop.loan_amount, prop.annual_interest_rate, prop.loan_term_years)
    starting_exit_value = max(prop.estimated_arv or 0.0, prop.purchase_price)
    for year in range(1, horizon + 1):
        income = gross_income * ((1.0 + prop.expected_annual_rent_growth) ** (year - 1))
        vacancy = income * prop.vacancy_rate
        effective_income = income - vacancy
        expense_base = non_management_expenses * ((1.0 + prop.expected_annual_expense_growth) ** (year - 1))
        management_fee = effective_income * prop.management_rate
        operating_expenses = expense_base + management_fee
        noi = effective_income - operating_expenses
        capital_reserve = max(prop.capex_annual, prop.rehab_budget * 0.025)
        cash_flow = noi - debt_service - capital_reserve
        loan_balance = remaining_loan_balance(prop.loan_amount, prop.annual_interest_rate, prop.loan_term_years, year)
        projected_value = starting_exit_value * ((1.0 + prop.expected_annual_appreciation) ** year)
        plan.append(
            OperatingPlanYear(
                year=year,
                gross_potential_income=income,
                vacancy_loss=vacancy,
                effective_gross_income=effective_income,
                operating_expenses=operating_expenses,
                noi=noi,
                debt_service=debt_service,
                capital_reserve=capital_reserve,
                cash_flow_before_tax=cash_flow,
                ending_loan_balance=loan_balance,
                projected_asset_value=projected_value,
            )
        )
    return plan


def average_dscr(plan: list[OperatingPlanYear]) -> float:
    if not plan:
        return 0.0
    return round(sum(year.debt_service_coverage() for year in plan) / len(plan), 3)


def minimum_dscr(plan: list[OperatingPlanYear]) -> float:
    if not plan:
        return 0.0
    return round(min(year.debt_service_coverage() for year in plan), 3)


def cumulative_cash_flow(plan: list[OperatingPlanYear]) -> float:
    return round(sum(year.cash_flow_before_tax for year in plan), 2)


def terminal_equity_value(plan: list[OperatingPlanYear], selling_cost_rate: float) -> float:
    if not plan:
        return 0.0
    terminal = plan[-1]
    return round(terminal.projected_asset_value * (1.0 - selling_cost_rate) - terminal.ending_loan_balance, 2)

