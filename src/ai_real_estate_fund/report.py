from __future__ import annotations

from .models import CommitteeDecision


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1%}"


def render_diligence_markdown(decision: CommitteeDecision) -> str:
    prop = decision.property
    metrics = decision.metrics
    dq = decision.data.data_quality
    lines: list[str] = []
    lines.append(f"# AI Real Estate Fund Diligence Memo: {prop.name}")
    lines.append("")
    lines.append(f"> {decision.disclaimer}")
    lines.append("")
    lines.append("## Committee Decision")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Run ID | `{decision.run_id}` |")
    lines.append(f"| Created | {decision.created_at} |")
    lines.append(f"| Recommendation | **{decision.recommendation.value}** |")
    lines.append(f"| Overall score | {decision.overall_score:.1f}/100 |")
    lines.append(f"| Suggested allocation | {decision.suggested_allocation_pct:.1f}% |")
    lines.append(f"| Max offer estimate | {money(decision.max_offer_price)} |")
    lines.append(f"| Margin of safety vs ask | {pct(decision.margin_of_safety)} |")
    if dq:
        lines.append(f"| Data completeness | {dq.completeness_score:.1f}/100 |")
        lines.append(f"| Evidence confidence | {dq.confidence_score:.1f}/100 |")
    lines.append("")

    lines.append("## Property Snapshot")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Address | {prop.address} |")
    lines.append(f"| Market | {prop.market} |")
    lines.append(f"| Type | {prop.property_type} |")
    lines.append(f"| Units | {prop.unit_count} |")
    if prop.square_feet:
        lines.append(f"| Square feet | {prop.square_feet:,.0f} |")
    if prop.year_built:
        lines.append(f"| Year built | {prop.year_built} |")
    lines.append(f"| Purchase price | {money(prop.purchase_price)} |")
    lines.append(f"| Estimated ARV | {money(prop.estimated_arv)} |")
    lines.append(f"| Monthly rent | {money(prop.monthly_rent)} |")
    lines.append(f"| Rehab budget | {money(prop.rehab_budget)} |")
    lines.append(f"| Loan amount | {money(prop.loan_amount)} |")
    lines.append("")

    lines.append("## Core Underwriting")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Gross potential income | {money(metrics.gross_potential_income)} |")
    lines.append(f"| Effective gross income | {money(metrics.effective_gross_income)} |")
    lines.append(f"| Operating expenses | {money(metrics.operating_expenses)} |")
    lines.append(f"| NOI | {money(metrics.noi)} |")
    lines.append(f"| Annual debt service | {money(metrics.annual_debt_service)} |")
    lines.append(f"| Cash flow before tax | {money(metrics.cash_flow_before_tax)} |")
    lines.append(f"| Cash invested | {money(metrics.cash_invested)} |")
    lines.append(f"| Cap rate | {pct(metrics.cap_rate)} |")
    lines.append(f"| Cash-on-cash return | {pct(metrics.cash_on_cash_return)} |")
    lines.append(f"| DSCR | {metrics.dscr:.2f}x |")
    lines.append(f"| Break-even occupancy | {pct(metrics.break_even_occupancy)} |")
    lines.append(f"| Projected sale price | {money(metrics.projected_sale_price)} |")
    lines.append(f"| Net sale proceeds | {money(metrics.projected_net_sale_proceeds)} |")
    lines.append(f"| Equity multiple | {metrics.equity_multiple:.2f}x |")
    lines.append(f"| Projected IRR | {pct(metrics.irr)} |")
    lines.append("")

    lines.append("## Agent Committee")
    lines.append("")
    lines.append("| Agent | Score | Recommendation | Confidence | Model |")
    lines.append("|---|---:|---:|---:|---:|")
    for finding in decision.findings:
        lines.append(
            f"| {finding.agent_name} | {finding.score:.1f} | {finding.recommendation.value} | "
            f"{pct(finding.confidence)} | {finding.model} |"
        )
    lines.append("")
    for finding in decision.findings:
        lines.append(f"### {finding.agent_name}")
        lines.append("")
        lines.append(f"_{finding.role}_")
        lines.append("")
        lines.append(finding.thesis)
        lines.append("")
        if finding.positives:
            lines.append("**Positives**")
            lines.append("")
            for item in finding.positives:
                lines.append(f"- {item}")
            lines.append("")
        if finding.concerns:
            lines.append("**Concerns**")
            lines.append("")
            for item in finding.concerns:
                lines.append(f"- {item}")
            lines.append("")
        if finding.actions:
            lines.append("**Required follow-up**")
            lines.append("")
            for item in finding.actions:
                lines.append(f"- {item}")
            lines.append("")
        if finding.evidence:
            lines.append("**Evidence used**")
            lines.append("")
            lines.append("| Source | Label | Value | Confidence |")
            lines.append("|---|---|---:|---:|")
            for evidence in finding.evidence[:8]:
                lines.append(
                    f"| {evidence.source} | {evidence.label} | {evidence.value} | {pct(evidence.confidence)} |"
                )
            lines.append("")

    lines.append("## Scenario Analysis")
    lines.append("")
    lines.append("| Scenario | Decision | Score | Cap Rate | CoC | DSCR | IRR | Cash Flow |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for scenario in decision.scenarios:
        lines.append(
            f"| {scenario.name} | {scenario.recommendation.value} | {scenario.score:.1f} | "
            f"{pct(scenario.cap_rate)} | {pct(scenario.cash_on_cash_return)} | "
            f"{scenario.dscr:.2f}x | {pct(scenario.irr)} | {money(scenario.cash_flow_before_tax)} |"
        )
    lines.append("")

    lines.append("## Data Quality and Audit Trail")
    lines.append("")
    if dq:
        lines.append(f"- Completeness score: **{dq.completeness_score:.1f}/100**")
        lines.append(f"- Evidence confidence score: **{dq.confidence_score:.1f}/100**")
        lines.append(f"- Evidence items captured: **{dq.evidence_count}**")
        if dq.missing_fields:
            lines.append("- Missing fields: " + ", ".join(dq.missing_fields))
        if dq.warnings:
            lines.append("- Warnings:")
            for warning in dq.warnings:
                lines.append(f"  - {warning}")
    lines.append("")

    lines.append("### Rent Comps")
    lines.append("")
    if decision.data.rent_comps:
        lines.append("| Address | Monthly Rent | Units | Distance | Confidence |")
        lines.append("|---|---:|---:|---:|---:|")
        for comp in decision.data.rent_comps:
            lines.append(
                f"| {comp.address} | {money(comp.monthly_rent)} | {comp.unit_count} | "
                f"{comp.distance_miles:.1f} mi | {pct(comp.confidence)} |"
            )
    else:
        lines.append("No rent comps available.")
    lines.append("")

    lines.append("### Sale Comps")
    lines.append("")
    if decision.data.sale_comps:
        lines.append("| Address | Sale Price | Units | PPSF | Distance | Confidence |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for comp in decision.data.sale_comps:
            ppsf = comp.price_per_sqft()
            ppsf_text = "n/a" if ppsf <= 0 else money(ppsf)
            lines.append(
                f"| {comp.address} | {money(comp.sale_price)} | {comp.unit_count} | {ppsf_text} | "
                f"{comp.distance_miles:.1f} mi | {pct(comp.confidence)} |"
            )
    else:
        lines.append("No sale comps available.")
    lines.append("")

    lines.append("## Risk Register")
    lines.append("")
    lines.append("| Risk | Severity | Probability | Mitigation |")
    lines.append("|---|---:|---:|---|")
    for risk in decision.risk_register:
        lines.append(f"| {risk.name} | {risk.severity} | {risk.probability} | {risk.mitigation} |")
    lines.append("")

    lines.append("## Thesis")
    lines.append("")
    lines.append(decision.thesis)
    lines.append("")
    lines.append("## Bear Case")
    lines.append("")
    lines.append(decision.bear_case)
    lines.append("")
    lines.append("## Recommended Next Steps")
    lines.append("")
    for step in decision.next_steps:
        lines.append(f"- {step}")
    lines.append("")
    if prop.notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(prop.notes)
        lines.append("")
    return "\n".join(lines)


# Backwards-compatible alias used by the optional backend export route.
def render_diligence_memo(decision: CommitteeDecision) -> str:
    return render_diligence_markdown(decision)
