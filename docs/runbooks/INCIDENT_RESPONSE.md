# Incident Response Runbook

## Severity levels

| Severity | Definition | Response |
|---|---|---|
| SEV1 | API unavailable, data corruption, audit-chain break, credential leak | Immediate rollback or isolation |
| SEV2 | Degraded analysis, database write failures, elevated error rates | Triage within one hour |
| SEV3 | Non-critical route failures or stale fixture data | Next business day |

## First 15 minutes

1. Confirm impact and start an incident log.
2. Check `/ops/health`, container logs, and recent deploys.
3. Verify whether audit logging is still recording events.
4. If secrets are exposed, rotate API keys immediately.
5. If analysis results may be wrong, disable external access and preserve logs.

## Useful commands

```bash
python -m ai_real_estate_fund health --json
python -m ai_real_estate_fund readiness --json
python -m ai_real_estate_fund audit-verify --json --strict
python scripts/smoke_test.py
```

## Recovery

Rollback to the previous image, restore from the latest verified backup if needed, and rerun the release checklist before re-opening access.
