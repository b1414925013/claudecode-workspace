FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY packages/env-service/ packages/env-service/

RUN uv sync --frozen --no-dev --package ksm-env

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8002

CMD ["uv", "run", "--package", "ksm-env", "uvicorn", "ksm_env.main:app", "--host", "0.0.0.0", "--port", "8002"]
