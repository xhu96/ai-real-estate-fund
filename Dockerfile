FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    SERVICE_NAME=ai-real-estate-fund

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY app ./app
COPY examples ./examples
COPY docs ./docs
COPY scripts ./scripts

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[api]" \
    && mkdir -p /app/data /app/reports \
    && chown -R app:app /app

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -m ai_real_estate_fund health --json >/tmp/health.json || exit 1

CMD ["uvicorn", "app.backend.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
