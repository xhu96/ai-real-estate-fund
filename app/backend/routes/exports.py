from __future__ import annotations
from fastapi import APIRouter, Depends, Response
from ai_real_estate_fund.investment_committee import run_property_committee
from ai_real_estate_fund.report import render_diligence_memo
from ai_real_estate_fund.report_pdf import render_report_pdf
from ..dependencies import require_scope
from ..utils.parsing import parse_property_input
router = APIRouter(prefix="/exports", tags=["exports"])


def _safe_filename(name: str) -> str:
    """Sanitize a property name into a filesystem/header-safe filename stem."""
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in (name or "report"))
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or "report"


@router.post("/memo.md")
def export_memo(payload: dict, _: dict = Depends(require_scope("export"))):
    decision = run_property_committee(parse_property_input(payload))
    return Response(render_diligence_memo(decision), media_type="text/markdown")


@router.post("/report.pdf")
def export_report_pdf(payload: dict, _: dict = Depends(require_scope("export"))):
    prop = parse_property_input(payload)
    decision = run_property_committee(prop)
    pdf_bytes = render_report_pdf(decision)
    filename = f"report-{_safe_filename(prop.name)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
