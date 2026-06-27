FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY packages/secret-service/ packages/secret-service/

RUN uv sync --frozen --no-dev --package ksm-secret

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8003

CMD ["uv", "run", "--package", "ksm-secret", "uvicorn", "ksm_secret.main:app", "--host", "0.0.0.0", "--port", "8003"]
