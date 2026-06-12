from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _split_csv(value: str | None, *, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if value is None or value.strip() == "":
        return default
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


@dataclass(frozen=True, slots=True)
class ConfigIssue:
    """Validation result for one deployment configuration control."""

    name: str
    severity: str
    message: str
    remediation: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProductionSettings:
    """Runtime settings shared by CLI production checks and the optional API.

    The project intentionally keeps the core package dependency-light. These
    settings are stdlib-only so readiness checks can run in CI before optional
    FastAPI, database, cloud, or observability dependencies are installed.
    """

    environment: str = "development"
    service_name: str = "ai-real-estate-fund"
    app_version: str = "0.6.0"
    release_sha: str = "local"

    database_url: str = "sqlite:///./data/app.db"
    audit_database_url: str = "sqlite:///./data/audit.db"
    artifact_root: Path = Path("reports")
    data_root: Path = Path("data")

    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1")

    api_keys: tuple[str, ...] = ()
    api_key_hashes: tuple[str, ...] = ()
    secret_key: str = "dev-secret-change-me"
    require_api_key: bool = False
    require_tls: bool = False

    enable_fixture_data: bool = True
    enable_demo_mode: bool = True
    require_human_approval_for_buy: bool = True

    log_level: str = "INFO"
    json_logs: bool = True
    metrics_enabled: bool = True
    sentry_dsn: str = ""

    rate_limit_per_minute: int = 120
    max_payload_bytes: int = 1_000_000
    request_timeout_seconds: int = 30
    data_retention_days: int = 365
    audit_retention_days: int = 2555

    model_name: str = "rules-v1"

    @classmethod
    def from_env(cls) -> "ProductionSettings":
        return cls(
            environment=os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower(),
            service_name=os.getenv("SERVICE_NAME", "ai-real-estate-fund"),
            app_version=os.getenv("APP_VERSION", "0.6.0"),
            release_sha=os.getenv("RELEASE_SHA", os.getenv("GIT_SHA", "local")),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
            audit_database_url=os.getenv("AUDIT_DATABASE_URL", "sqlite:///./data/audit.db"),
            artifact_root=Path(os.getenv("ARTIFACT_ROOT", "reports")),
            data_root=Path(os.getenv("DATA_ROOT", "data")),
            cors_origins=_split_csv(os.getenv("CORS_ORIGINS"), default=("http://localhost:5173",)),
            allowed_hosts=_split_csv(os.getenv("ALLOWED_HOSTS"), default=("localhost", "127.0.0.1")),
            api_keys=_split_csv(os.getenv("API_KEYS")),
            api_key_hashes=_split_csv(os.getenv("API_KEY_HASHES")),
            secret_key=os.getenv("SECRET_KEY", "dev-secret-change-me"),
            require_api_key=_bool_env("REQUIRE_API_KEY", False),
            require_tls=_bool_env("REQUIRE_TLS", False),
            enable_fixture_data=_bool_env("ENABLE_FIXTURE_DATA", True),
            enable_demo_mode=_bool_env("ENABLE_DEMO_MODE", True),
            require_human_approval_for_buy=_bool_env("REQUIRE_HUMAN_APPROVAL_FOR_BUY", True),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            json_logs=_bool_env("JSON_LOGS", True),
            metrics_enabled=_bool_env("METRICS_ENABLED", True),
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            rate_limit_per_minute=_int_env("RATE_LIMIT_PER_MINUTE", 120),
            max_payload_bytes=_int_env("MAX_PAYLOAD_BYTES", 1_000_000),
            request_timeout_seconds=_int_env("REQUEST_TIMEOUT_SECONDS", 30),
            data_retention_days=_int_env("DATA_RETENTION_DAYS", 365),
            audit_retention_days=_int_env("AUDIT_RETENTION_DAYS", 2555),
            model_name=os.getenv("MODEL_NAME", "rules-v1"),
        )

    @property
    def is_production(self) -> bool:
        return self.environment in {"production", "prod"}

    @property
    def is_ci(self) -> bool:
        return self.environment in {"ci", "test"} or bool(os.getenv("CI"))

    def validate(self) -> list[ConfigIssue]:
        issues: list[ConfigIssue] = []
        envs = {"development", "test", "ci", "staging", "production", "prod"}
        if self.environment not in envs:
            issues.append(ConfigIssue("environment", "fail", f"Unsupported APP_ENV: {self.environment}", "Use development, test, ci, staging, or production."))

        if self.is_production and self.secret_key in {"", "dev-secret-change-me", "changeme", "secret"}:
            issues.append(ConfigIssue("secret_key", "fail", "SECRET_KEY is missing or uses the development default.", "Generate a high-entropy SECRET_KEY in your secret manager."))
        elif len(self.secret_key) < 16:
            issues.append(ConfigIssue("secret_key_length", "warn", "SECRET_KEY is short.", "Use at least 32 random bytes encoded as hex or base64."))

        if self.is_production and not (self.api_keys or self.api_key_hashes):
            issues.append(ConfigIssue("api_keys", "fail", "No API key material configured in production.", "Set API_KEY_HASHES or API_KEYS and REQUIRE_API_KEY=true."))
        if self.is_production and not self.require_api_key:
            issues.append(ConfigIssue("api_key_required", "fail", "REQUIRE_API_KEY is disabled in production.", "Set REQUIRE_API_KEY=true."))

        if self.is_production and "*" in self.cors_origins:
            issues.append(ConfigIssue("cors_origins", "fail", "Wildcard CORS is not allowed in production.", "Set explicit HTTPS origins."))
        if self.is_production and "*" in self.allowed_hosts:
            issues.append(ConfigIssue("allowed_hosts", "fail", "Wildcard allowed hosts are not allowed in production.", "Set explicit hostnames."))
        if self.is_production and self.enable_demo_mode:
            issues.append(ConfigIssue("demo_mode", "fail", "ENABLE_DEMO_MODE is enabled in production.", "Disable demo mode for production."))
        if self.is_production and self.enable_fixture_data:
            issues.append(ConfigIssue("fixture_data", "warn", "Fixture data is enabled in production.", "Use licensed data providers and set ENABLE_FIXTURE_DATA=false."))
        if self.is_production and self.database_url.startswith("sqlite"):
            issues.append(ConfigIssue("database_url", "warn", "SQLite is configured for production.", "Use a managed Postgres-compatible DATABASE_URL for multi-user deployments."))
        if self.is_production and not self.require_tls:
            issues.append(ConfigIssue("tls", "warn", "REQUIRE_TLS is disabled.", "Terminate TLS at the load balancer and set REQUIRE_TLS=true."))
        if self.max_payload_bytes <= 0 or self.max_payload_bytes > 25_000_000:
            issues.append(ConfigIssue("max_payload_bytes", "warn", "Payload limit is missing or unusually high.", "Set MAX_PAYLOAD_BYTES to a small value such as 1000000."))
        if self.rate_limit_per_minute <= 0:
            issues.append(ConfigIssue("rate_limit", "fail", "RATE_LIMIT_PER_MINUTE must be positive.", "Set a positive per-principal limit."))
        if self.data_retention_days <= 0:
            issues.append(ConfigIssue("data_retention", "warn", "DATA_RETENTION_DAYS is not positive.", "Define a retention policy that fits your legal obligations."))
        if not self.require_human_approval_for_buy:
            issues.append(ConfigIssue("human_approval", "warn", "BUY recommendations can be emitted without a human approval gate.", "Keep REQUIRE_HUMAN_APPROVAL_FOR_BUY=true for production workflows."))
        return issues

    def redacted(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["secret_key"] = "***" if self.secret_key else ""
        payload["api_keys"] = tuple("***" for _ in self.api_keys)
        payload["api_key_hashes"] = tuple(hash_value[:10] + "..." for hash_value in self.api_key_hashes)
        payload["artifact_root"] = str(self.artifact_root)
        payload["data_root"] = str(self.data_root)
        return payload
