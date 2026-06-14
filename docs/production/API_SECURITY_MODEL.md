# API Security Model

The API uses scoped API keys. Scopes are:

| Scope | Use |
|---|---|
| `read` | health, readiness, config-free operational reads |
| `write` | create saved resources |
| `analyze` | run institutional analysis |
| `export` | generate memo/export artifacts |
| `admin` | all scopes and administrative endpoints |

Routes that mutate state or expose operational details must use `Depends(require_scope(...))`.

Development mode can run in demo mode. Production must require scoped keys.
