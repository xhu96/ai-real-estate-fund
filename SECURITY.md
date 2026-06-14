# Security Policy

## Supported versions

The `main` branch and the latest tagged release are supported for security fixes.

## Reporting a vulnerability

Open a private security advisory on GitHub or contact the repository owner directly. Do not disclose exploitable details in public issues.

## Security posture

The repository includes:

- scoped API-key authentication, fail-closed in deployed environments (local/test is open for demo; `staging`/`production` require a valid key via `REQUIRE_API_KEY=true` and `API_KEY_HASHES`)
- request validation (malformed payloads return 422, not 500) and a non-leaking error handler
- security headers
- request size limits
- in-memory rate limiting (keyed on client IP)
- PII and secret redaction helpers
- audit logging with hash-chain verification
- production-readiness checks
- Docker non-root runtime (`USER app`)
- backup/restore and incident-response runbooks

## Known boundaries

- The default local database is SQLite. Multi-user production should use managed database infrastructure and backup policies.
- The in-memory rate limiter is per process. Multi-replica production should use an API gateway or shared limiter.
- Fixture data is not investment-grade. Production should use licensed data providers.
- The model does not provide financial, legal, tax, lending, or investment advice.
