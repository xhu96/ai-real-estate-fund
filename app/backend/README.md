# Backend

FastAPI façade over the core `ai_real_estate_fund` package. The backend separates HTTP routes, middleware, persistence, repositories, and services so the core agents remain reusable from CLI, tests, notebooks, or workers.

## Production v6 routes

- `GET /ops/health`
- `GET /ops/ready`
- `GET /ops/metrics`
- `GET /ops/audit/verify`
- `POST /v6/institutional/analyze`
- `POST /v6/institutional/memo.md`

## Production middleware

- request ID
- process timing
- security headers
- request size limit
- rate limiting
- audit logging
- exception normalization

## Run

```bash
python -m pip install -e ".[api]"
uvicorn app.backend.main:create_app --factory --reload
```
