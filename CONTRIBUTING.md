# Contributing

Contributions are welcome. Please keep the project educational, auditable, and deterministic by default.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

Optional extras:

```bash
python -m pip install -e ".[api]"
```

## Guidelines

- Keep financial calculations deterministic and covered by tests.
- Keep agent scoring explainable; every score should produce positives, concerns, evidence, and follow-up actions.
- Do not present outputs as financial advice.
- Mark fixture data clearly as fixture data.
- Do not add scraping integrations unless the source permits it.
- Add or update tests when changing underwriting math, agent scoring, data providers, or API behavior.
- Preserve the offline demo path; LLM calls must stay optional and may never alter deterministic scores.

## Pull request checklist

- [ ] `python -m pytest -q` passes.
- [ ] New agents include evidence and a confidence score.
- [ ] New data providers include source and timestamp metadata where possible.
- [ ] User-facing text keeps the educational disclaimer intact.
- [ ] README/docs are updated when commands or outputs change.
