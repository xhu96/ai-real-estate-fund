# Security Policy

## Supported versions

The `main` branch and the latest tagged release are supported for security fixes.

## Reporting a vulnerability

Open a private security advisory on GitHub or contact the repository owner directly. Do not disclose exploitable details in public issues.

## Security posture in v6

The repository includes:

- scoped API-key authentication
- security headers
- request size limits
- in-memory rate limiting
- PII and secret redaction helpers
- audit logging with hash-chain verification
- production-readiness checks
- Docker non-root runtime
- Kubernetes manifests with restricted security context examples
- backup/restore and incident-response runbooks

## Known boundaries

- The default local database is SQLite. Multi-user production should use managed database infrastructure and backup policies.
- The in-memory rate limiter is per process. Multi-replica production should use an API gateway or shared limiter.
- Fixture data is not investment-grade. Production should use licensed data providers.
- The model does not provide financial, legal, tax, lending, or investment advice.
