# ───────────────────────────────────────────────
# Stage base: dependencias Python con Poetry
# ───────────────────────────────────────────────
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock* ./

# ───────────────────────────────────────────────
# Stage development: incluye dev deps + hot reload
# ───────────────────────────────────────────────
FROM base AS development

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ───────────────────────────────────────────────
# Stage production: sin dev deps, workers múltiples
# ───────────────────────────────────────────────
FROM base AS production

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

COPY . .

EXPOSE 8000

# Usar Gunicorn como process manager para los workers de Uvicorn en producción
# Se asume que 'gunicorn' está en las dependencias de pyproject.toml
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:8000"]
