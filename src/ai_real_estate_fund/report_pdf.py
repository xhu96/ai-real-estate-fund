"""Server-side PDF report renderer for committee decisions.

`render_report_pdf` accepts either a committee decision *object* (screening
``CommitteeDecision`` or ``InstitutionalDecision``) or an already-normalized
decision ``dict``. Internally it works off ``decision.to_dict()`` so the two
institutional/screening shapes can be laid out with one uniform code path.

The renderer is intentionally defensive: institutional and screening payloads
differ (the institutional shape carries ``scorecards``/``policy_results`` the
screening shape lacks), so every field access goes through ``.get`` with a
sane fallback and every numeric formatter guards ``None``/``inf``/``nan``.

Only fpdf2 (pure-python, no system dependencies) is used.
"""

from __future__ import annotations

import math
from typing import Any

from fpdf import FPDF

# fpdf2's core fonts are Latin-1 only. Decision text comes from rules/LLM output
# and may contain unicode punctuation (curly quotes, en dashes, bullets); coerce
# anything outside Latin-1 to a safe ASCII-ish equivalent so output never raises.
_UNICODE_FALLBACKS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", "…": "...",
    "•": "-", " ": " ", " ": " ", " ": " ",
    "×": "x", "→": "->",
}

# Palette (RGB).
_INK = (17, 24, 39)
_MUTED = (107, 114, 128)
_ACCENT = (30, 58, 138)
_RULE = (209, 213, 219)
_BAND = (243, 244, 246)


def _safe_text(value: Any) -> str:
    """Return a Latin-1-encodable string for fpdf2 core fonts."""
    text = "" if value is None else str(value)
    for bad, good in _UNICODE_FALLBACKS.items():
        if bad in text:
            text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _money(value: Any) -> str:
    if not _is_finite_number(value):
        return "n/a"
    return f"${value:,.0f}"


def _pct(value: Any) -> str:
    if not _is_finite_number(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def _ratio(value: Any) -> str:
    if not _is_finite_number(value):
        return "n/a"
    return f"{value:.2f}x"


def _num(value: Any, digits: int = 1) -> str:
    if not _is_finite_number(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _as_decision_dict(decision: Any) -> dict[str, Any]:
    if isinstance(decision, dict):
        return decision
    to_dict = getattr(decision, "to_dict", None)
    if callable(to_dict):
        result = to_dict()
        if isinstance(result, dict):
            return result
    raise TypeError("render_report_pdf expects a decision object with to_dict() or a dict")


class _Report(FPDF):
    """A4 portrait document with a running footer."""

    def __init__(self, property_name: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._property_name = property_name
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(left=16, top=16, right=16)
        self.set_title(_safe_text(f"Investment Report - {property_name}"))

    @property
    def usable_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def footer(self) -> None:  # noqa: D401 - fpdf2 hook name
        self.set_y(-15)
        self.set_font("Helvetica", size=7)
        self.set_text_color(*_MUTED)
        label = _safe_text(f"AI Real Estate Fund  |  {self._property_name}")
        self.cell(0, 5, label, align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")
        self.set_text_color(*_INK)


def _section_title(pdf: _Report, text: str) -> None:
    if pdf.get_y() > pdf.h - 40:
        pdf.add_page()
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*_ACCENT)
    pdf.cell(0, 7, _safe_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*_RULE)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(2)
    pdf.set_text_color(*_INK)


def _body_text(pdf: _Report, text: str, size: float = 9.5) -> None:
    clean = _safe_text(text).strip()
    if not clean:
        return
    pdf.set_font("Helvetica", size=size)
    pdf.set_text_color(*_INK)
    pdf.multi_cell(pdf.usable_width, 5, clean, new_x="LMARGIN", new_y="NEXT")


def _kv_table(pdf: _Report, rows: list[tuple[str, str]]) -> None:
    """Two-column label/value table with zebra banding."""
    if not rows:
        return
    label_w = pdf.usable_width * 0.42
    value_w = pdf.usable_width - label_w
    line_h = 6.0
    for idx, (label, value) in enumerate(rows):
        if pdf.get_y() > pdf.h - 28:
            pdf.add_page()
        if idx % 2 == 0:
            pdf.set_fill_color(*_BAND)
            fill = True
        else:
            fill = False
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*_INK)
        pdf.cell(label_w, line_h, _safe_text(label), border=0, fill=fill)
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(*_MUTED)
        pdf.cell(value_w, line_h, _safe_text(value), border=0, fill=fill,
                 new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.set_text_color(*_INK)
    pdf.ln(1)


def _row_table(pdf: _Report, headers: list[tuple[str, float]], rows: list[list[str]]) -> None:
    """Generic multi-column table. `headers` is (label, relative_weight)."""
    if not rows:
        return
    total_weight = sum(weight for _, weight in headers) or 1.0
    widths = [pdf.usable_width * (weight / total_weight) for _, weight in headers]
    line_h = 5.8
    if pdf.get_y() > pdf.h - 28:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*_ACCENT)
    pdf.set_text_color(255, 255, 255)
    for (label, _), width in zip(headers, widths):
        pdf.cell(width, line_h, _safe_text(label), border=0, fill=True, align="L")
    pdf.ln(line_h)
    pdf.set_text_color(*_INK)
    for idx, row in enumerate(rows):
        if pdf.get_y() > pdf.h - 24:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_fill_color(*_ACCENT)
            pdf.set_text_color(255, 255, 255)
            for (label, _), width in zip(headers, widths):
                pdf.cell(width, line_h, _safe_text(label), border=0, fill=True, align="L")
            pdf.ln(line_h)
            pdf.set_text_color(*_INK)
        fill = idx % 2 == 0
        pdf.set_fill_color(*_BAND)
        pdf.set_font("Helvetica", size=8.5)
        for cell, width in zip(row, widths):
            pdf.cell(width, line_h, _safe_text(cell), border=0, fill=fill, align="L")
        pdf.ln(line_h)
    pdf.ln(1)


def _header_block(pdf: _Report, data: dict[str, Any], prop: dict[str, Any]) -> None:
    name = prop.get("name") or data.get("run_id") or "Investment Report"
    engine = "Institutional Committee" if "scorecards" in data else "Property Committee"
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*_MUTED)
    pdf.cell(0, 5, _safe_text(f"AI Real Estate Fund  -  {engine}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*_INK)
    pdf.multi_cell(pdf.usable_width, 8, _safe_text(str(name)), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*_MUTED)
    meta_bits = []
    if data.get("run_id"):
        meta_bits.append(f"Run {data['run_id']}")
    if data.get("created_at"):
        meta_bits.append(str(data["created_at"]))
    if meta_bits:
        pdf.cell(0, 5, _safe_text("  |  ".join(meta_bits)), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_INK)
    pdf.ln(2)


def _recommendation_band(pdf: _Report, data: dict[str, Any]) -> None:
    rec = _safe_text(data.get("recommendation") or "n/a")
    score = data.get("overall_score")
    pdf.set_fill_color(*_ACCENT)
    pdf.set_text_color(255, 255, 255)
    band_h = 16.0
    x0, y0 = pdf.l_margin, pdf.get_y()
    pdf.rect(x0, y0, pdf.usable_width, band_h, style="F")
    half = pdf.usable_width / 2
    pdf.set_xy(x0 + 3, y0 + 2)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(half - 3, 5, "RECOMMENDATION", new_x="LEFT", new_y="NEXT")
    pdf.set_x(x0 + 3)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(half - 3, 7, rec)
    pdf.set_xy(x0 + half, y0 + 2)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(half - 3, 5, "OVERALL SCORE", align="R", new_x="LEFT", new_y="NEXT")
    pdf.set_x(x0 + half)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(half - 3, 7, _safe_text(f"{_num(score)}/100"), align="R")
    pdf.set_xy(x0, y0 + band_h)
    pdf.set_text_color(*_INK)
    pdf.ln(4)


def _property_rows(prop: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if prop.get("address"):
        rows.append(("Address", str(prop["address"])))
    if prop.get("market"):
        rows.append(("Market", str(prop["market"])))
    if prop.get("property_type"):
        rows.append(("Property type", str(prop["property_type"]).replace("_", " ").title()))
    if prop.get("unit_count") is not None:
        rows.append(("Units", str(prop["unit_count"])))
    if prop.get("square_feet"):
        rows.append(("Square feet", f"{prop['square_feet']:,.0f}"))
    if prop.get("year_built"):
        rows.append(("Year built", str(prop["year_built"])))
    if prop.get("purchase_price"):
        rows.append(("Purchase price", _money(prop.get("purchase_price"))))
    if prop.get("estimated_arv"):
        rows.append(("Estimated ARV", _money(prop.get("estimated_arv"))))
    if prop.get("loan_amount"):
        rows.append(("Loan amount", _money(prop.get("loan_amount"))))
    return rows


def _metric_rows(metrics: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        ("Cap rate", _pct(metrics.get("cap_rate"))),
        ("Cash-on-cash return", _pct(metrics.get("cash_on_cash_return"))),
        ("DSCR", _ratio(metrics.get("dscr"))),
        ("Projected IRR", _pct(metrics.get("irr"))),
        ("Equity multiple", _ratio(metrics.get("equity_multiple"))),
        ("Net operating income", _money(metrics.get("noi"))),
        ("Effective gross income", _money(metrics.get("effective_gross_income"))),
        ("Operating expenses", _money(metrics.get("operating_expenses"))),
        ("Annual debt service", _money(metrics.get("annual_debt_service"))),
        ("Cash flow before tax", _money(metrics.get("cash_flow_before_tax"))),
        ("Total project cost", _money(metrics.get("total_project_cost"))),
        ("Cash invested", _money(metrics.get("cash_invested"))),
        ("Loan-to-cost", _pct(metrics.get("loan_to_cost"))),
        ("Break-even occupancy", _pct(metrics.get("break_even_occupancy"))),
    ]


def render_report_pdf(decision: Any) -> bytes:
    """Render a committee decision into a professional PDF and return raw bytes.

    Accepts a screening ``CommitteeDecision``, an ``InstitutionalDecision``, or a
    pre-normalized decision ``dict``. Missing/None fields are handled gracefully.
    """
    data = _as_decision_dict(decision)
    prop = data.get("property") or {}
    metrics = data.get("metrics") or {}
    property_name = _safe_text(str(prop.get("name") or "Investment Report"))

    pdf = _Report(property_name)
    pdf.add_page()

    _header_block(pdf, data, prop)
    _recommendation_band(pdf, data)

    # Property -----------------------------------------------------------
    _section_title(pdf, "Property")
    _kv_table(pdf, _property_rows(prop))

    # Key metrics --------------------------------------------------------
    _section_title(pdf, "Key Metrics")
    _kv_table(pdf, _metric_rows(metrics))

    # Investment thesis --------------------------------------------------
    thesis = data.get("thesis")
    if thesis:
        _section_title(pdf, "Investment Thesis")
        _body_text(pdf, thesis)

    bear_case = data.get("bear_case")
    if bear_case:
        _section_title(pdf, "Bear Case")
        _body_text(pdf, bear_case)

    # Scorecards (institutional) or top findings (screening) -------------
    scorecards = data.get("scorecards") or []
    if scorecards:
        _section_title(pdf, "Scorecards")
        rows = [
            [_safe_text(card.get("name") or card.get("category") or "Scorecard"),
             _num(card.get("score"))]
            for card in scorecards[:10]
        ]
        _row_table(pdf, [("Scorecard", 4.0), ("Score", 1.0)], rows)
    else:
        findings = data.get("findings") or []
        if findings:
            _section_title(pdf, "Top Findings")
            ranked = sorted(
                findings,
                key=lambda f: f.get("score") if _is_finite_number(f.get("score")) else 0.0,
                reverse=True,
            )
            rows = [
                [_safe_text(f.get("agent_name") or "Agent"),
                 _safe_text(str(f.get("recommendation") or "")),
                 _num(f.get("score"))]
                for f in ranked[:8]
            ]
            _row_table(pdf, [("Finding", 3.0), ("Call", 1.4), ("Score", 1.0)], rows)

    # Scenarios ----------------------------------------------------------
    scenarios = data.get("scenarios") or []
    if scenarios:
        _section_title(pdf, "Scenarios")
        rows = [
            [_safe_text(s.get("name") or "Scenario"),
             _safe_text(str(s.get("recommendation") or "")),
             _num(s.get("score")),
             _pct(s.get("cap_rate")),
             _ratio(s.get("dscr")),
             _pct(s.get("irr"))]
            for s in scenarios[:8]
        ]
        _row_table(
            pdf,
            [("Scenario", 2.6), ("Call", 1.4), ("Score", 1.0),
             ("Cap", 1.0), ("DSCR", 1.0), ("IRR", 1.0)],
            rows,
        )

    # Risk register ------------------------------------------------------
    risks = data.get("risk_register") or []
    if risks:
        _section_title(pdf, "Top Risks")
        rows = [
            [_safe_text(r.get("name") or "Risk"),
             _safe_text(str(r.get("severity") or "")),
             _safe_text(str(r.get("probability") or ""))]
            for r in risks[:10]
        ]
        _row_table(pdf, [("Risk", 4.0), ("Severity", 1.2), ("Likelihood", 1.2)], rows)

    # Next steps ---------------------------------------------------------
    next_steps = data.get("next_steps") or []
    if next_steps:
        _section_title(pdf, "Recommended Next Steps")
        pdf.set_font("Helvetica", size=9.5)
        for step in next_steps[:12]:
            text = _safe_text(str(step)).strip()
            if not text:
                continue
            if pdf.get_y() > pdf.h - 24:
                pdf.add_page()
            pdf.multi_cell(pdf.usable_width, 5, f"-  {text}", new_x="LMARGIN", new_y="NEXT")

    # Disclaimer ---------------------------------------------------------
    disclaimer = data.get("disclaimer")
    if disclaimer:
        _section_title(pdf, "Disclaimer")
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*_MUTED)
        pdf.multi_cell(pdf.usable_width, 4.5, _safe_text(disclaimer), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*_INK)

    output = pdf.output()
    return bytes(output)
