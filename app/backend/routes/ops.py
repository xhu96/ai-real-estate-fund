from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from ai_real_estate_fund.production import ProductionReadinessChecker, render_readiness_markdown, run_health_checks
from ai_real_estate_fund.production.audit import SQLiteAuditLog
from ai_real_estate_fund.production.observability import metrics
from ..dependencies import require_scope
from ..settings import settings

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/health")
def health():
    return run_health_checks(settings.production).to_dict()


@router.get("/ready")
def ready(_: dict = Depends(require_scope("read"))):
    report = ProductionReadinessChecker(root=".", settings=settings.production).run()
    return report.to_dict()


@router.get("/ready.md")
def ready_markdown(_: dict = Depends(require_scope("read"))):
    report = ProductionReadinessChecker(root=".", settings=settings.production).run()
    return Response(render_readiness_markdown(report), media_type="text/markdown")


@router.get("/metrics")
def prometheus_metrics():
    return Response(metrics.to_prometheus(), media_type="text/plain; version=0.0.4")


@router.get("/config")
def redacted_config(_: dict = Depends(require_scope("admin"))):
    return settings.production.redacted()


@router.get("/audit/verify")
def audit_verify(_: dict = Depends(require_scope("admin"))):
    path = settings.production.audit_database_url.replace("sqlite:///", "")
    ok, errors = SQLiteAuditLog(path).verify_chain()
    return {"ok": ok, "errors": errors}
