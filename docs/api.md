# API

Start the backend:

```bash
python -m pip install -e ".[api]"
uvicorn app.backend.main:create_app --factory --reload
```

## Core endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | legacy health check |
| `POST` | `/analyses` | run screening committee analysis and persist result |
| `GET` | `/analyses` | list recent analyses |
| `GET` | `/comps/{market}` | fixture rent and sale comps |
| `POST` | `/scenarios` | scenario analysis |
| `POST` | `/portfolio/optimize` | portfolio allocation optimizer |
| `POST` | `/exports/memo.md` | markdown memo export |

## Production endpoints

| Method | Path | Scope | Description |
|---|---|---|---|
| `GET` | `/ops/health` | public | runtime health |
| `GET` | `/ops/ready` | `read` | readiness JSON |
| `GET` | `/ops/ready.md` | `read` | readiness markdown |
| `GET` | `/ops/metrics` | public | Prometheus metrics |
| `GET` | `/ops/config` | `admin` | redacted runtime configuration |
| `GET` | `/ops/audit/verify` | `admin` | audit hash-chain verification |
| `POST` | `/institutional/analyze` | `analyze` | institutional diligence payload; `?llm=true` adds analyst commentary |
| `POST` | `/institutional/memo.md` | `export` | institutional markdown memo |

## Auth

Production mode requires an `X-API-Key` header.

```bash
curl -H "X-API-Key: $AI_REF_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/duplex_sunbelt.json \
  http://localhost:8000/institutional/analyze
```

Use `Idempotency-Key` on analysis requests that may be retried by clients.
