# syntax=docker/dockerfile:1
# Build context = repository root. Uses Next.js standalone output.

FROM node:20-alpine AS build
RUN corepack enable
WORKDIR /repo
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/developer-portal ./apps/developer-portal
RUN pnpm install --frozen-lockfile --filter @smart-city/developer-portal... \
    && pnpm --filter @smart-city/developer-portal build

FROM node:20-alpine
RUN apk add --no-cache curl && adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=build /repo/apps/developer-portal/.next/standalone ./
COPY --from=build /repo/apps/developer-portal/.next/static ./apps/developer-portal/.next/static
USER appuser
ENV NODE_ENV=production PORT=3001 HOSTNAME=0.0.0.0
EXPOSE 3001
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:3001/api/health || exit 1
CMD ["node", "apps/developer-portal/server.js"]
