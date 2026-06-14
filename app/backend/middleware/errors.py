from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from ..logging_config import get_logger

logger = get_logger("app.backend.errors")


def register_exception_handlers(app):
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"error": "validation_error", "detail": str(exc), "request_id": getattr(request.state, "request_id", "")})

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError):
        request_id = getattr(request.state, "request_id", "")
        # The detail is surfaced intentionally (e.g. config errors) but the
        # failure must also be observable in logs with its request_id.
        logger.warning("runtime error handling request: %s", exc, extra={"request_id": request_id}, exc_info=exc)
        return JSONResponse(status_code=500, content={"error": "runtime_error", "detail": str(exc), "request_id": request_id})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "")
        # Log the full stack for operators; return a generic body so no
        # internal detail or stack leaks to the client. FastAPI handles
        # HTTPException itself, so 401/422/etc. never reach this catch-all.
        logger.exception("unhandled error handling request", extra={"request_id": request_id})
        return JSONResponse(status_code=500, content={"error": "internal_error", "request_id": request_id})
