from __future__ import annotations

from ai_real_estate_fund.production.audit import AuditEvent, SQLiteAuditLog
from ai_real_estate_fund.production.privacy import redact_payload
from ..settings import settings


def _audit_path() -> str:
    url = settings.production.audit_database_url
    return url.replace("sqlite:///", "") if url.startswith("sqlite:///") else "data/audit.db"


async def audit_requests(request, call_next):
    response = await call_next(request)
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            audit = SQLiteAuditLog(_audit_path())
            audit.append(AuditEvent(
                actor=getattr(request.state, "actor", "anonymous"),
                action=f"http.{request.method.lower()}",
                resource_type="http_route",
                resource_id=str(request.url.path),
                request_id=getattr(request.state, "request_id", ""),
                payload=redact_payload({"status_code": response.status_code, "query": dict(request.query_params)}),
            ))
        except Exception:
            # Audit failure must be observable but should not leak internals to the user.
            response.headers["X-Audit-Status"] = "failed"
        else:
            response.headers["X-Audit-Status"] = "recorded"
    return response
