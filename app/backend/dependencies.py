from __future__ import annotations

from fastapi import Header, HTTPException, Request, status

from ai_real_estate_fund.production.auth import build_store
from .settings import settings


def get_api_key_store():
    return build_store(settings.production.api_keys, settings.production.api_key_hashes)


def require_scope(required_scope: str):
    def dependency(request: Request, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        prod = settings.production
        # Demo mode is fail-OPEN in local/test environments only. Any deployed
        # environment (staging, production) or unknown APP_ENV falls through to
        # key verification. See ProductionSettings.allows_demo_mode.
        if prod.allows_demo_mode:
            request.state.actor = "demo"
            return {"name": "demo", "scopes": ["read", "write", "analyze", "export"]}
        result = get_api_key_store().verify(x_api_key, required_scope=required_scope)
        if not result.ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.reason or "unauthorized")
        request.state.actor = result.principal.name if result.principal else "api-key"
        return result.principal.to_dict() if result.principal else {"name": "unknown"}
    return dependency
