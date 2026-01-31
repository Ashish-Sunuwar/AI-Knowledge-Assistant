# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- runtime (production image) ----
FROM python:3.12-slim AS runtime
WORKDIR /app

RUN useradd -m appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only what production needs
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser data ./data

USER appuser

ENV ENVIRONMENT=production
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- test stage (includes tests) ----
FROM runtime AS test

# tests need to exist in the image
COPY --chown=appuser:appuser tests ./tests

# Avoid pytest cache permission issues
ENV PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest_cache"

# Default envs for deterministic test runs
ENV LLM_PROVIDER=stub
ENV RAG_MIN_SCORE=0.12
ENV DISABLE_RATE_LIMIT=true
ENV ENABLE_TRUSTED_HOSTS=false

CMD ["python", "-m", "pytest", "-q"]