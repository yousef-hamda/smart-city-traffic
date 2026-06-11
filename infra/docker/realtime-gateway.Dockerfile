# syntax=docker/dockerfile:1
# Build context = repository root.

FROM node:20-alpine AS build
RUN corepack enable
WORKDIR /repo
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/realtime-gateway ./apps/realtime-gateway
RUN pnpm install --frozen-lockfile --filter @smart-city/realtime-gateway... \
    && pnpm --filter @smart-city/realtime-gateway build \
    && pnpm --filter @smart-city/realtime-gateway --prod deploy /out

FROM node:20-alpine
RUN apk add --no-cache curl && adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=build /out .
USER appuser
ENV NODE_ENV=production PORT=8088
EXPOSE 8088
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:8088/health || exit 1
CMD ["node", "dist/server.js"]
