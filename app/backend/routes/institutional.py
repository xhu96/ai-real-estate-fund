from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.llm import client_from_options
from ai_real_estate_fund.institutional.memo import render_institutional_memo
from ai_real_estate_fund.report_pdf import render_report_pdf
from ai_real_estate_fund.production.audit import AuditEvent, SQLiteAuditLog
from ai_real_estate_fund.production.model_risk import evaluate_decision_payload
from ai_real_estate_fund.production.observability import track_timing
from ai_real_estate_fund.production.reliability import IdempotencyStore
from ai_real_estate_fund.production.privacy import redact_payload
from ..dependencies import require_scope
from ..repositories.analysis_repository import AnalysisRepository
from ..settings import settings
from ..utils.parsing import parse_property_input

router = APIRouter(prefix="/institutional", tags=["institutional"])
_idempotency_store = IdempotencyStore()


def _audit_path() -> str:
    return settings.production.audit_database_url.replace("sqlite:///", "")


def _safe_filename(name: str) -> str:
    """Sanitize a property name into a filesystem/header-safe filename stem."""
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in (name or "report"))
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or "report"


@router.post("/analyze")
def analyze(payload: dict, llm: bool = False, llm_provider: str | None = None, llm_model: str | None = None, principal: dict = Depends(require_scope("analyze")), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), x_llm_key: str | None = Header(default=None, alias="X-LLM-Key"), x_llm_base: str | None = Header(default=None, alias="X-LLM-Base")):
    if idempotency_key:
        cached = _idempotency_store.get(idempotency_key)
        if isinstance(cached, dict):
            return cached
    prop = parse_property_input(payload)
    llm_client = None
    if llm:
        try:
            llm_client = client_from_options(provider=llm_provider, api_key=x_llm_key, model=llm_model, base_url=x_llm_base)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with track_timing("institutional_analysis", labels={"market": prop.market}):
        decision = run_institutional_committee(prop, llm_client=llm_client)
    result = decision.to_dict()
    result["requires_human_approval"] = settings.production.require_human_approval_for_buy
    result["model_risk"] = evaluate_decision_payload(result).to_dict()
    result.setdefault("engine", "institutional")
    try:  # best-effort persistence: institutional runs should appear in Runs/Dashboard
        AnalysisRepository().save(result)
    except Exception:  # noqa: BLE001 - persistence failure must not break the 200 response
        pass
    SQLiteAuditLog(_audit_path()).append(AuditEvent(
        actor=str(principal.get("name", "api")),
        action="institutional.analyze",
        resource_type="property",
        resource_id=prop.name,
        payload=redact_payload({"market": prop.market, "recommendation": result["recommendation"], "overall_score": result["overall_score"]}),
    ))
    if idempotency_key:
        _idempotency_store.set(idempotency_key, result)
    return result


@router.post("/memo.md")
def memo(payload: dict, llm: bool = False, llm_provider: str | None = None, llm_model: str | None = None, _: dict = Depends(require_scope("export")), x_llm_key: str | None = Header(default=None, alias="X-LLM-Key"), x_llm_base: str | None = Header(default=None, alias="X-LLM-Base")):
    prop = parse_property_input(payload)
    llm_client = None
    if llm:
        try:
            llm_client = client_from_options(provider=llm_provider, api_key=x_llm_key, model=llm_model, base_url=x_llm_base)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with track_timing("institutional_memo_export", labels={"market": prop.market}):
        decision = run_institutional_committee(prop, llm_client=llm_client)
    return Response(render_institutional_memo(decision), media_type="text/markdown")


@router.post("/report.pdf")
def report_pdf(payload: dict, llm: bool = False, llm_provider: str | None = None, llm_model: str | None = None, _: dict = Depends(require_scope("export")), x_llm_key: str | None = Header(default=None, alias="X-LLM-Key"), x_llm_base: str | None = Header(default=None, alias="X-LLM-Base")):
    prop = parse_property_input(payload)
    llm_client = None
    if llm:
        try:
            llm_client = client_from_options(provider=llm_provider, api_key=x_llm_key, model=llm_model, base_url=x_llm_base)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with track_timing("institutional_report_pdf", labels={"market": prop.market}):
        decision = run_institutional_committee(prop, llm_client=llm_client)
    pdf_bytes = render_report_pdf(decision)
    filename = f"report-{_safe_filename(prop.name)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
