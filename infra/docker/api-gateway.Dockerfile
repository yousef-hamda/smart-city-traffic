# syntax=docker/dockerfile:1
# Build context = repository root.

FROM node:20-alpine AS build
RUN corepack enable
WORKDIR /repo
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/api-gateway ./apps/api-gateway
RUN pnpm install --frozen-lockfile --filter @smart-city/api-gateway... \
    && pnpm --filter @smart-city/api-gateway build \
    && pnpm --filter @smart-city/api-gateway --prod deploy /out

FROM node:20-alpine
RUN apk add --no-cache curl && adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=build /out .
USER appuser
ENV NODE_ENV=production PORT=8080
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:8080/health || exit 1
CMD ["node", "dist/main.js"]
