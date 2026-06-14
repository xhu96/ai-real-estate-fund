from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Header, HTTPException

from ai_real_estate_fund.llm import client_from_options, list_models, provider_status
from ..dependencies import require_scope

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status")
def status(provider: str | None = None, _: dict = Depends(require_scope("read"))):
    """Resolved provider, whether a server key is present, base URL and default model (no secrets)."""
    return provider_status(provider)


@router.get("/models")
def models(
    provider: str | None = None,
    x_llm_key: str | None = Header(default=None, alias="X-LLM-Key"),
    x_llm_base: str | None = Header(default=None, alias="X-LLM-Base"),
    _: dict = Depends(require_scope("read")),
):
    """List model ids from the provider catalog. Uses the override key/base when supplied, else the .env key."""
    try:
        ids = list_models(provider=provider, api_key=x_llm_key, base_url=x_llm_base)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"provider": (provider or provider_status().get("provider")), "count": len(ids), "models": ids}


@router.post("/test")
def test(
    provider: str | None = None,
    model: str | None = None,
    x_llm_key: str | None = Header(default=None, alias="X-LLM-Key"),
    x_llm_base: str | None = Header(default=None, alias="X-LLM-Base"),
    _: dict = Depends(require_scope("analyze")),
):
    """Fire one tiny completion to confirm the credentials/model work end-to-end."""
    try:
        client = client_from_options(provider=provider, api_key=x_llm_key, model=model, base_url=x_llm_base)
        started = time.time()
        sample = client.complete("Reply with the single word OK.", "ping", temperature=0)
        return {"ok": True, "model": client.model, "latency_ms": int((time.time() - started) * 1000), "sample": sample[:120]}
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
