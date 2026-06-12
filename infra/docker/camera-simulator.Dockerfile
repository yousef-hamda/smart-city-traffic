# syntax=docker/dockerfile:1
# Build context = repository root.

FROM python:3.11-slim AS build
WORKDIR /app
COPY apps/camera-simulator/pyproject.toml ./
COPY apps/camera-simulator/src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim
# opencv-python-headless still needs libglib2.0; ffmpeg enables the RTSP sink.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser
COPY --from=build /install /usr/local
USER appuser
ENTRYPOINT ["python", "-m", "camera_simulator"]
CMD ["run"]
