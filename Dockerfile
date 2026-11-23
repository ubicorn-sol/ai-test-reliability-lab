FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.9.0 /uv /usr/local/bin/uv
WORKDIR /app

ENV UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-cache

COPY tests/reference/test_bola.py tests/reference/
CMD ["sh", "-ec", ": ${VAMPI_SECURE_URL:?Set VAMPI_SECURE_URL to the private secure test target}; exec .venv/bin/python -m pytest tests/reference/test_bola.py -v"]
