from __future__ import annotations

from fastapi.responses import JSONResponse

from ai_real_estate_fund.production.rate_limit import InMemoryRateLimiter
from ..settings import settings

_limiter = InMemoryRateLimiter(limit=settings.production.rate_limit_per_minute, window_seconds=60)


async def enforce_request_limits(request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.production.max_payload_bytes:
        return JSONResponse(status_code=413, content={"error": "payload_too_large"})
    principal = request.headers.get("x-api-key") or request.client.host if request.client else "anonymous"
    decision = _limiter.check(principal)
    if not decision.allowed:
        return JSONResponse(status_code=429, content={"error": "rate_limited"}, headers={"Retry-After": str(int(decision.retry_after_seconds))})
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
    return response
