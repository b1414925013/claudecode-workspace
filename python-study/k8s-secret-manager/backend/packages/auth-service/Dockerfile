FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY packages/auth-service/ packages/auth-service/

RUN uv sync --frozen --no-dev --package ksm-auth

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001

CMD ["uv", "run", "--package", "ksm-auth", "uvicorn", "ksm_auth.main:app", "--host", "0.0.0.0", "--port", "8001"]
