# syntax=docker/dockerfile:1
# Build context = repository root. Uses Next.js standalone output.

FROM node:20-alpine AS build
RUN corepack enable
WORKDIR /repo
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages ./packages
COPY apps/frontend ./apps/frontend
RUN pnpm install --frozen-lockfile --filter @smart-city/frontend... \
    && pnpm --filter @smart-city/frontend build

FROM node:20-alpine
RUN apk add --no-cache curl && adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=build /repo/apps/frontend/.next/standalone ./
COPY --from=build /repo/apps/frontend/.next/static ./apps/frontend/.next/static
COPY --from=build /repo/apps/frontend/public ./apps/frontend/public
USER appuser
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -sf http://localhost:3000/api/health || exit 1
CMD ["node", "apps/frontend/server.js"]
