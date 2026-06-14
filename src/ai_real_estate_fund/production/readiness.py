from __future__ import annotations

import importlib.util
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .health import run_health_checks
from .settings import ConfigIssue, ProductionSettings


@dataclass(frozen=True, slots=True)
class ReadinessCheck:
    category: str
    name: str
    status: str
    message: str
    remediation: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProductionReadinessReport:
    generated_at: str
    environment: str
    score: float
    passed: bool
    checks: list[ReadinessCheck] = field(default_factory=list)

    @property
    def failures(self) -> list[ReadinessCheck]:
        return [check for check in self.checks if check.status == "fail"]

    @property
    def warnings(self) -> list[ReadinessCheck]:
        return [check for check in self.checks if check.status == "warn"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "environment": self.environment,
            "score": self.score,
            "passed": self.passed,
            "failures": len(self.failures),
            "warnings": len(self.warnings),
            "checks": [check.to_dict() for check in self.checks],
        }


def _issue_to_check(issue: ConfigIssue) -> ReadinessCheck:
    return ReadinessCheck(category="configuration", name=issue.name, status=issue.severity, message=issue.message, remediation=issue.remediation)


class ProductionReadinessChecker:
    def __init__(self, root: str | Path = ".", settings: ProductionSettings | None = None) -> None:
        self.root = Path(root)
        self.settings = settings or ProductionSettings.from_env()

    def _file_check(self, relative_path: str, *, category: str, required: bool = True, message: str = "") -> ReadinessCheck:
        path = self.root / relative_path
        exists = path.exists()
        if exists:
            return ReadinessCheck(category=category, name=relative_path, status="pass", message=message or f"{relative_path} exists")
        return ReadinessCheck(
            category=category,
            name=relative_path,
            status="fail" if required else "warn",
            message=f"{relative_path} is missing",
            remediation=f"Add {relative_path} before deploying.",
        )

    def _docs_checks(self) -> list[ReadinessCheck]:
        docs = [
            "README.md",
            "SECURITY.md",
            "LICENSE",
            "docs/production/PRODUCTION_READINESS.md",
            "docs/runbooks/INCIDENT_RESPONSE.md",
            "docs/runbooks/BACKUP_RESTORE.md",
            "docs/production/DATA_GOVERNANCE.md",
            "docs/production/MODEL_RISK_MANAGEMENT.md",
            "docs/production/RELEASE_CHECKLIST.md",
        ]
        return [self._file_check(path, category="documentation") for path in docs]

    def _deployment_checks(self) -> list[ReadinessCheck]:
        files = [
            "Dockerfile",
            "docker-compose.yml",
            "compose.production.yml",
            ".github/workflows/tests.yml",
            ".github/workflows/production.yml",
            "scripts/preflight.py",
            "scripts/smoke_test.py",
        ]
        return [self._file_check(path, category="deployment") for path in files]

    def _package_checks(self) -> list[ReadinessCheck]:
        checks: list[ReadinessCheck] = []
        package_available = importlib.util.find_spec("ai_real_estate_fund") is not None
        checks.append(ReadinessCheck("package", "importable", "pass" if package_available else "fail", "Core package can be imported." if package_available else "Core package is not importable.", "Install with python -m pip install -e ."))
        tests_dir = self.root / "tests"
        test_count = len(list(tests_dir.glob("test_*.py"))) if tests_dir.exists() else 0
        checks.append(ReadinessCheck("testing", "unit_tests", "pass" if test_count >= 10 else "warn", f"{test_count} unit test modules found.", "Add tests for underwriting, policy gates, API, security, and production controls."))
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            text = pyproject.read_text(encoding="utf-8")
            placeholders = [marker for marker in ("Your Name", "your-username") if marker in text]
            status = "warn" if placeholders else "pass"
            checks.append(ReadinessCheck("release", "metadata_placeholders", status, "Package metadata checked.", "Replace pyproject placeholders before public release." if placeholders else ""))
        return checks

    def _health_checks(self) -> list[ReadinessCheck]:
        health = run_health_checks(self.settings)
        checks: list[ReadinessCheck] = []
        for item in health.checks:
            status = "pass" if item.status in {"ok", "unknown"} else "fail"
            checks.append(ReadinessCheck("runtime", item.name, status, item.message))
        return checks

    def run(self) -> ProductionReadinessReport:
        checks: list[ReadinessCheck] = []
        checks.extend(_issue_to_check(issue) for issue in self.settings.validate())
        checks.extend(self._docs_checks())
        checks.extend(self._deployment_checks())
        checks.extend(self._package_checks())
        checks.extend(self._health_checks())

        if not any(check.status == "fail" for check in checks):
            passed = True
        else:
            passed = False
        total = len(checks) or 1
        penalty = sum(1.0 if check.status == "fail" else 0.35 if check.status == "warn" else 0.0 for check in checks)
        score = round(max(0.0, 100.0 * (1 - penalty / total)), 1)
        return ProductionReadinessReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            environment=self.settings.environment,
            score=score,
            passed=passed,
            checks=checks,
        )


def render_readiness_markdown(report: ProductionReadinessReport) -> str:
    lines = [
        "# Production Readiness Report",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Environment: `{report.environment}`",
        f"- Score: **{report.score:.1f}/100**",
        f"- Passed: **{report.passed}**",
        f"- Failures: **{len(report.failures)}**",
        f"- Warnings: **{len(report.warnings)}**",
        "",
        "| Category | Check | Status | Message | Remediation |",
        "|---|---|---:|---|---|",
    ]
    for check in report.checks:
        lines.append(f"| {check.category} | {check.name} | {check.status.upper()} | {check.message} | {check.remediation} |")
    lines.append("")
    return "\n".join(lines)
