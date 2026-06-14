# Release Checklist

## Before merge

- [ ] Unit tests pass locally.
- [ ] API imports successfully.
- [ ] Production readiness passes in CI mode.
- [ ] Smoke test passes on the example deal.
- [ ] New settings have safe defaults.
- [ ] New routes are protected by `require_scope` or explicitly public.
- [ ] New state-changing routes emit audit events.
- [ ] New data fields are documented.

## Before production deploy

- [ ] `APP_ENV=production` readiness output reviewed.
- [ ] API keys rotated and stored in secret manager.
- [ ] `ENABLE_DEMO_MODE=false`.
- [ ] `REQUIRE_API_KEY=true`.
- [ ] `REQUIRE_TLS=true`.
- [ ] CORS origins are exact HTTPS origins.
- [ ] Backups are configured and restore was tested.
- [ ] Monitoring alerts are configured.
- [ ] Incident owner and escalation path are known.
- [ ] Human approval workflow is operational.

## After deploy

- [ ] `/ops/health` returns healthy.
- [ ] `/ops/ready` has no unexpected failures.
- [ ] `/ops/metrics` is scraped.
- [ ] Audit chain verifies.
- [ ] One smoke analysis completes in staging/production.
