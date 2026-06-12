# Deployment

## Docker Compose

```bash
cp .env.production.example .env.production
# edit .env.production
APP_ENV=production docker compose -f compose.production.yml up --build
```

## Preflight

```bash
APP_ENV=production python scripts/preflight.py --strict
```

Use a managed database and managed secrets for serious multi-user deployments.
