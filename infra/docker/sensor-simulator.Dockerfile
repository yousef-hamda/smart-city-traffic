# syntax=docker/dockerfile:1
# Build context = repository root.

FROM python:3.11-slim AS build
WORKDIR /app
COPY apps/sensor-simulator/pyproject.toml ./
COPY apps/sensor-simulator/src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
RUN useradd --create-home --uid 10001 appuser
COPY --from=build /install /usr/local
USER appuser
ENTRYPOINT ["python", "-m", "simulator"]
CMD ["run"]
