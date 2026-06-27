FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY packages/toolbox-service/ packages/toolbox-service/

RUN uv sync --frozen --no-dev --package ksm-toolbox

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8004

CMD ["uv", "run", "--package", "ksm-toolbox", "uvicorn", "ksm_toolbox.main:app", "--host", "0.0.0.0", "--port", "8004"]
