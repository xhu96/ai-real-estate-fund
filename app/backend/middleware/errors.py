from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app):
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"error": "validation_error", "detail": str(exc), "request_id": getattr(request.state, "request_id", "")})

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request: Request, exc: RuntimeError):
        return JSONResponse(status_code=500, content={"error": "runtime_error", "detail": str(exc), "request_id": getattr(request.state, "request_id", "")})
