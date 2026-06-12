# Data Governance

The default project uses fixtures so contributors can run the repository without API keys. A real deployment must replace fixture adapters with permissioned, licensed, and monitored data providers.

## Required governance controls

1. Maintain a data-source inventory with owner, license, refresh cadence, retention period, and allowed use.
2. Capture `source`, `as_of`, and `confidence` for each diligence evidence item.
3. Flag stale rent comps, sale comps, tax data, insurance quotes, and debt quotes.
4. Retain audit logs for the configured `AUDIT_RETENTION_DAYS`.
5. Redact PII from logs and model prompts.
6. Document the legal basis for storing property-owner, tenant, borrower, or contact data.

## Fixture data policy

Production should set:

```bash
ENABLE_FIXTURE_DATA=false
```

If fixture data remains enabled, the readiness check emits a warning because the output is not investment-grade.
