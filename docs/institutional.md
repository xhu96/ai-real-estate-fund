# Institutional Committee Architecture

The institutional committee expands the project from a deterministic property analyzer into a larger
production-style alpha with an institutional investment-committee workflow.

## Main additions

- 77 specialist diligence workstreams organized across acquisition, income, expenses,
  debt, physical condition, market, portfolio, and governance workstreams.
- Investment-policy gates with hard stops and warning-level breaches.
- Inferred data-room manifest and document-readiness scoring.
- Capital-stack model with senior debt, common equity, and reserve layers.
- Operating plan with year-by-year EGI, NOI, DSCR, cash flow, loan balance,
  and projected value.
- Larger underwriting and research packages for detailed model components.
- API service routes and React dashboard surfaces.

## Command

```bash
python -m ai_real_estate_fund institutional examples/duplex_sunbelt.json
```

## Safety

This is still an educational alpha. The workflow is deterministic and uses
fixture/manual inputs by default. A real deployment needs licensed data,
source-document verification, access controls, security review, model-risk
management, legal review, and professional sign-off.

