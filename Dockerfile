FROM python:3.14-slim

# Copiamos uv desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 1) Solo dependencias (esta capa se cachea si pyproject/uv.lock no cambian)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Código de la aplicación
COPY src ./src

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["fastapi", "run", "src/api/main.py", "--host", "0.0.0.0", "--port", "8000"]
