# syntax=docker/dockerfile:1
# Build context = repository root.

FROM python:3.11-slim AS build
WORKDIR /app
COPY apps/ml-prediction/pyproject.toml ./
COPY apps/ml-prediction/src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser
COPY --from=build /install /usr/local
USER appuser
EXPOSE 8083
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:8083/health || exit 1
CMD ["uvicorn", "ml_prediction.main:app", "--host", "0.0.0.0", "--port", "8083"]
