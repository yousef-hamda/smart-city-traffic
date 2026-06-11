# Developer Portal

Public-facing Next.js app for external API consumers.

> **Phase 1 skeleton.** Serves a landing page and `/api/health`. The full
> portal lands in Phase 16: API catalog auto-rendered from the federated
> OpenAPI + GraphQL schemas, API key management, usage dashboards, code
> samples (cURL/JS/Python/Java), embedded Swagger UI + GraphiQL, and the
> pricing-tier mock.

## Environment

| Variable              | Default                 | Purpose              |
| --------------------- | ----------------------- | -------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080` | API gateway base URL |

## Local development

```bash
pnpm install
pnpm --filter @smart-city/developer-portal dev   # http://localhost:3001
```
