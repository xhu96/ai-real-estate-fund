from __future__ import annotations

from math import isfinite

from .models import PropertyInput, UnderwritingMetrics


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def annual_debt_service(loan_amount: float, annual_interest_rate: float, loan_term_years: int) -> float:
    """Return annual mortgage payment for a fully amortizing loan."""
    if loan_amount <= 0:
        return 0.0
    months = loan_term_years * 12
    monthly_rate = annual_interest_rate / 12
    if monthly_rate == 0:
        return loan_amount / months * 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / (
        (1 + monthly_rate) ** months - 1
    )
    return monthly_payment * 12


def remaining_loan_balance(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    years_elapsed: int,
) -> float:
    if loan_amount <= 0:
        return 0.0
    months_total = loan_term_years * 12
    months_elapsed = min(max(years_elapsed * 12, 0), months_total)
    monthly_rate = annual_interest_rate / 12
    if months_elapsed >= months_total:
        return 0.0
    if monthly_rate == 0:
        principal_paid = loan_amount * (months_elapsed / months_total)
        return max(0.0, loan_amount - principal_paid)
    payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** months_total) / (
        (1 + monthly_rate) ** months_total - 1
    )
    balance = loan_amount * (1 + monthly_rate) ** months_elapsed - payment * (
        ((1 + monthly_rate) ** months_elapsed - 1) / monthly_rate
    )
    return max(0.0, balance)


def estimate_irr(cash_flows: list[float]) -> float | None:
    """Estimate annual IRR using bisection.

    Returns None when cash flows do not have a valid sign change or the solution
    is outside a practical range.
    """
    if not cash_flows or not any(cf < 0 for cf in cash_flows) or not any(cf > 0 for cf in cash_flows):
        return None

    def npv(rate: float) -> float:
        return sum(cf / ((1 + rate) ** idx) for idx, cf in enumerate(cash_flows))

    low, high = -0.95, 2.0
    low_npv, high_npv = npv(low), npv(high)
    if not (isfinite(low_npv) and isfinite(high_npv)) or low_npv * high_npv > 0:
        return None
    for _ in range(120):
        mid = (low + high) / 2
        mid_npv = npv(mid)
        if abs(mid_npv) < 1e-7:
            return mid
        if low_npv * mid_npv <= 0:
            high = mid
            high_npv = mid_npv
        else:
            low = mid
            low_npv = mid_npv
    return (low + high) / 2


def project_annual_cash_flows(prop: PropertyInput) -> list[float]:
    """Build project-level cash flows: year 0 investment, operating cash flows, sale."""
    base = underwrite_property(prop)
    cash_flows = [-base.cash_invested]
    annual_debt = base.annual_debt_service
    gross_income = base.gross_potential_income
    fixed_expenses_without_mgmt = (
        prop.property_taxes_annual
        + prop.insurance_annual
        + prop.repairs_annual
        + prop.utilities_annual
        + prop.hoa_annual
        + prop.capex_annual
    )
    for year in range(1, prop.holding_period_years + 1):
        income = gross_income * ((1 + prop.expected_annual_rent_growth) ** (year - 1))
        vacancy_loss = income * prop.vacancy_rate
        egi = income - vacancy_loss
        non_mgmt_expenses = fixed_expenses_without_mgmt * (
            (1 + prop.expected_annual_expense_growth) ** (year - 1)
        )
        management_fee = egi * prop.management_rate
        noi = egi - non_mgmt_expenses - management_fee
        annual_cash_flow = noi - annual_debt
        if year == prop.holding_period_years:
            annual_cash_flow += base.projected_net_sale_proceeds
        cash_flows.append(annual_cash_flow)
    return cash_flows


def underwrite_property(prop: PropertyInput) -> UnderwritingMetrics:
    prop.validate()
    gross_potential_income = (prop.monthly_rent + prop.other_monthly_income) * 12
    vacancy_loss = gross_potential_income * prop.vacancy_rate
    effective_gross_income = gross_potential_income - vacancy_loss
    management_fee = effective_gross_income * prop.management_rate
    operating_expenses = (
        prop.property_taxes_annual
        + prop.insurance_annual
        + prop.repairs_annual
        + prop.utilities_annual
        + prop.hoa_annual
        + prop.capex_annual
        + management_fee
    )
    noi = effective_gross_income - operating_expenses
    debt_service = annual_debt_service(prop.loan_amount, prop.annual_interest_rate, prop.loan_term_years)
    cash_flow_before_tax = noi - debt_service
    total_project_cost = prop.purchase_price + prop.acquisition_costs + prop.rehab_budget
    cash_invested = max(0.0, total_project_cost - prop.loan_amount)
    loan_to_cost = prop.loan_amount / total_project_cost if total_project_cost else 0.0
    cap_rate = noi / prop.purchase_price if prop.purchase_price else 0.0
    cash_on_cash_return = cash_flow_before_tax / cash_invested if cash_invested else 0.0
    dscr = noi / debt_service if debt_service else float("inf")
    break_even_occupancy = (
        (operating_expenses + debt_service) / gross_potential_income if gross_potential_income else 1.0
    )

    starting_exit_value = max(prop.estimated_arv or 0.0, prop.purchase_price)
    projected_sale_price = starting_exit_value * (
        (1 + prop.expected_annual_appreciation) ** prop.holding_period_years
    )
    projected_loan_balance = remaining_loan_balance(
        prop.loan_amount,
        prop.annual_interest_rate,
        prop.loan_term_years,
        prop.holding_period_years,
    )
    projected_net_sale_proceeds = (
        projected_sale_price * (1 - prop.selling_cost_rate) - projected_loan_balance
    )

    cash_flows = [-cash_invested]
    annual_debt = debt_service
    fixed_expenses_without_mgmt = (
        prop.property_taxes_annual
        + prop.insurance_annual
        + prop.repairs_annual
        + prop.utilities_annual
        + prop.hoa_annual
        + prop.capex_annual
    )
    cumulative_distributions = 0.0
    for year in range(1, prop.holding_period_years + 1):
        income = gross_potential_income * ((1 + prop.expected_annual_rent_growth) ** (year - 1))
        egi = income * (1 - prop.vacancy_rate)
        expenses = fixed_expenses_without_mgmt * (
            (1 + prop.expected_annual_expense_growth) ** (year - 1)
        ) + egi * prop.management_rate
        annual_noi = egi - expenses
        annual_cash = annual_noi - annual_debt
        if year == prop.holding_period_years:
            annual_cash += projected_net_sale_proceeds
        cumulative_distributions += annual_cash
        cash_flows.append(annual_cash)

    equity_multiple = cumulative_distributions / cash_invested if cash_invested else 0.0
    irr = estimate_irr(cash_flows)

    return UnderwritingMetrics(
        gross_potential_income=gross_potential_income,
        vacancy_loss=vacancy_loss,
        effective_gross_income=effective_gross_income,
        operating_expenses=operating_expenses,
        management_fee=management_fee,
        noi=noi,
        annual_debt_service=debt_service,
        cash_flow_before_tax=cash_flow_before_tax,
        total_project_cost=total_project_cost,
        cash_invested=cash_invested,
        loan_to_cost=loan_to_cost,
        cap_rate=cap_rate,
        cash_on_cash_return=cash_on_cash_return,
        dscr=dscr,
        break_even_occupancy=break_even_occupancy,
        projected_sale_price=projected_sale_price,
        projected_loan_balance=projected_loan_balance,
        projected_net_sale_proceeds=projected_net_sale_proceeds,
        equity_multiple=equity_multiple,
        irr=irr,
    )


def max_price_for_target_cap_rate(prop: PropertyInput, target_cap_rate: float = 0.075) -> float:
    """Estimate max purchase price from stabilized NOI and target cap rate."""
    if target_cap_rate <= 0:
        raise ValueError("target_cap_rate must be positive")
    metrics = underwrite_property(prop)
    max_price = metrics.noi / target_cap_rate if metrics.noi > 0 else 0.0
    return max(0.0, max_price - prop.rehab_budget * 0.25)
