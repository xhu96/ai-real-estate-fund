from __future__ import annotations


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the api extra: python -m pip install -e '.[api]'") from exc

    from .database.migrations import migrate
    from .logging_config import configure_logging
    from .middleware.audit import audit_requests
    from .middleware.errors import register_exception_handlers
    from .middleware.request_id import add_request_id
    from .middleware.request_limits import enforce_request_limits
    from .middleware.security_headers import add_security_headers
    from .middleware.timing import add_timing_header
    from .routes import analyses, comps, exports, health, ops, portfolio, properties, scenarios, storage, validation, watchlist
    from .routes import committee, institutional, llm, research
    from .settings import settings

    configure_logging()
    migrate()
    app = FastAPI(
        title=settings.app_name,
        version=settings.production.app_version,
        docs_url="/docs" if settings.production.enable_demo_mode else None,
        redoc_url="/redoc" if settings.production.enable_demo_mode else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID", "Idempotency-Key", "X-LLM-Key", "X-LLM-Base"],
    )
    app.middleware("http")(audit_requests)
    app.middleware("http")(enforce_request_limits)
    app.middleware("http")(add_security_headers)
    app.middleware("http")(add_timing_header)
    app.middleware("http")(add_request_id)
    register_exception_handlers(app)

    routers = [
        health.router,
        ops.router,
        properties.router,
        analyses.router,
        comps.router,
        scenarios.router,
        portfolio.router,
        exports.router,
        storage.router,
        validation.router,
        watchlist.router,
        institutional.router,
        llm.router,
        research.router,
        committee.router,
    ]
    for router in routers:
        app.include_router(router)

    # Single-server mode: when the frontend has been built, serve it same-origin so
    # one process hosts both the API and the UI (no CORS, no API-base to configure,
    # works on any port). Mounted AFTER the API routers, so they take precedence.
    # Skipped when there is no build (dev with Vite, or tests) — the API still runs alone.
    from pathlib import Path

    from fastapi.staticfiles import StaticFiles

    dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
    return app


app = create_app()
