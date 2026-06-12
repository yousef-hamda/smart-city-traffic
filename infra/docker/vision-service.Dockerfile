# syntax=docker/dockerfile:1
# Build context = repository root.

FROM python:3.11-slim AS build
WORKDIR /app
COPY apps/vision-service/pyproject.toml ./
COPY apps/vision-service/src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
# curl for the healthcheck; libglib2.0 is required by opencv-python-headless.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser
COPY --from=build /install /usr/local
USER appuser
EXPOSE 8082
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:8082/health || exit 1
CMD ["uvicorn", "vision_service.main:app", "--host", "0.0.0.0", "--port", "8082"]
