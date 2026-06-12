from __future__ import annotations


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the api extra: python -m pip install -e '.[api]'") from exc

    from .database.migrations import migrate
    from .middleware.audit import audit_requests
    from .middleware.errors import register_exception_handlers
    from .middleware.request_id import add_request_id
    from .middleware.request_limits import enforce_request_limits
    from .middleware.security_headers import add_security_headers
    from .middleware.timing import add_timing_header
    from .routes import analyses, comps, exports, health, ops, portfolio, properties, scenarios, storage, validation, watchlist
    from .routes import institutional
    from .settings import settings

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
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID", "Idempotency-Key"],
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
    ]
    for router in routers:
        app.include_router(router)
    return app


app = create_app()
