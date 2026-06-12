# Security Hardening

## Authentication

The API supports scoped API keys. Use `scripts/rotate_api_key.py` to generate a raw key and a SHA-256 hash. Store the raw key only in your secret manager and deploy the hash through `API_KEY_HASHES`.

Development mode can run without an API key. Production must set:

```bash
REQUIRE_API_KEY=true
ENABLE_DEMO_MODE=false
```

## Transport security

Set `REQUIRE_TLS=true` and terminate TLS at the platform ingress, reverse proxy, or load balancer.

## Payload controls

Set `MAX_PAYLOAD_BYTES` to restrict uploaded property/deal payload size. The API also applies a per-principal in-memory rate limiter. Multi-replica production should use a shared limiter such as Redis or an API gateway quota policy.

## Headers

The FastAPI app emits security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Cache-Control: no-store`

## Audit

State-changing HTTP methods are recorded in the SQLite audit log with a hash chain. Run:

```bash
python -m ai_real_estate_fund audit-verify --strict
```

## Secrets

Never commit `.env.production`. Commit only `.env.production.example`. Rotate API keys before adding external users or moving from staging to production.
