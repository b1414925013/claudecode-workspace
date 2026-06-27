FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY packages/api-gateway/ packages/api-gateway/
COPY scripts/init_db.py scripts/init_db.py

RUN uv sync --frozen --no-dev --package ksm-gateway

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "--package", "ksm-gateway", "uvicorn", "ksm_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
