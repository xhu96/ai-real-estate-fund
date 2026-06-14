from __future__ import annotations

from time import perf_counter

from ai_real_estate_fund.production.observability import metrics


async def add_timing_header(request, call_next):
    start = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{duration_ms:.2f}"
    metrics.inc("ai_real_estate_fund_requests_total", labels={"method": request.method, "path": request.url.path, "status": str(response.status_code)})
    metrics.set("ai_real_estate_fund_last_request_duration_ms", duration_ms, labels={"method": request.method, "path": request.url.path})
    return response
