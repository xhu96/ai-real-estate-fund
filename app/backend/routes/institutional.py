from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response

from ai_real_estate_fund.committee import run_institutional_committee
from ai_real_estate_fund.llm import live_client_from_env
from ai_real_estate_fund.institutional.memo import render_institutional_memo
from ai_real_estate_fund.models import PropertyInput
from ai_real_estate_fund.production.audit import AuditEvent, SQLiteAuditLog
from ai_real_estate_fund.production.model_risk import evaluate_decision_payload
from ai_real_estate_fund.production.observability import track_timing
from ai_real_estate_fund.production.reliability import IdempotencyStore
from ai_real_estate_fund.production.privacy import redact_payload
from ..dependencies import require_scope
from ..settings import settings

router = APIRouter(prefix="/institutional", tags=["institutional"])
_idempotency_store = IdempotencyStore()


def _audit_path() -> str:
    return settings.production.audit_database_url.replace("sqlite:///", "")


@router.post("/analyze")
def analyze(payload: dict, llm: bool = False, llm_provider: str | None = None, llm_model: str | None = None, principal: dict = Depends(require_scope("analyze")), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if idempotency_key:
        cached = _idempotency_store.get(idempotency_key)
        if isinstance(cached, dict):
            return cached
    prop = PropertyInput.from_dict(payload)
    llm_client = None
    if llm:
        try:
            llm_client = live_client_from_env(model=llm_model, provider=llm_provider)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with track_timing("institutional_analysis", labels={"market": prop.market}):
        decision = run_institutional_committee(prop, llm_client=llm_client)
    result = decision.to_dict()
    result["requires_human_approval"] = settings.production.require_human_approval_for_buy
    result["model_risk"] = evaluate_decision_payload(result).to_dict()
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
def memo(payload: dict, llm: bool = False, llm_provider: str | None = None, llm_model: str | None = None, _: dict = Depends(require_scope("export"))):
    prop = PropertyInput.from_dict(payload)
    llm_client = None
    if llm:
        try:
            llm_client = live_client_from_env(model=llm_model, provider=llm_provider)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with track_timing("institutional_memo_export", labels={"market": prop.market}):
        decision = run_institutional_committee(prop, llm_client=llm_client)
    return Response(render_institutional_memo(decision), media_type="text/markdown")
