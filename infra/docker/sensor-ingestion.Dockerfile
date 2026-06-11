# syntax=docker/dockerfile:1
# Build context = repository root:
#   docker build -f infra/docker/sensor-ingestion.Dockerfile -t smart-city/sensor-ingestion .

# ---- Build stage ----
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace

# Cache dependencies separately from sources
COPY apps/sensor-ingestion/pom.xml ./
RUN mvn -q -B dependency:go-offline

COPY apps/sensor-ingestion/src ./src
RUN mvn -q -B package -DskipTests

# ---- Runtime stage ----
FROM eclipse-temurin:21-jre

# curl is needed for the container HEALTHCHECK
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app app

WORKDIR /app
COPY --from=build /workspace/target/sensor-ingestion-*.jar app.jar

USER app

# 8081 = HTTP (REST + actuator), 9091 = gRPC (Phase 2)
EXPOSE 8081 9091

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:8081/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
