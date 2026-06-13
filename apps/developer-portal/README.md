# Developer Portal (Phase 16)

Public-facing Next.js 14 application for external API consumers of the Smart City Traffic platform. Provides an API catalog, interactive REST + GraphQL explorer, client-side API key management, code samples, and pricing information.

## Features

- **API Catalog** — all REST endpoints grouped by resource (auth, segments, incidents, alerts, predictions, assistant), auto-rendered from a typed TypeScript spec
- **Interactive Explorer** — embedded Swagger UI (dynamic import, SSR disabled) pointed at `/openapi.json`; GraphQL federated schema SDL viewer with example queries
- **API Key Management** — generate, scope, copy, and revoke keys (client-side mock using `crypto.randomUUID`); usage breakdown table
- **Code Samples** — `cURL / JavaScript / Python / Java` tabs per endpoint with syntax highlighting via `prism-react-renderer v2`
- **Pricing** — Free / Pro / Enterprise tier cards
- **Health check** — `GET /api/health` returns service status

## Stack

| Layer               | Technology                                         |
| ------------------- | -------------------------------------------------- |
| Framework           | Next.js 14 App Router, TypeScript strict mode      |
| Styling             | Tailwind CSS v3 (slate/indigo/violet dark theme)   |
| API Explorer        | swagger-ui-react v5 (dynamic import, SSR disabled) |
| Syntax highlighting | prism-react-renderer v2                            |
| Testing             | Jest 29 + Testing Library React 14                 |

## Project structure

```
apps/developer-portal/
├── app/
│   ├── globals.css           Tailwind directives
│   ├── layout.tsx            Root layout (dark theme + TopNav)
│   ├── page.tsx              API Catalog landing page
│   ├── explore/
│   │   ├── page.tsx          Interactive explorer (REST + GraphQL)
│   │   └── SwaggerPanel.tsx  Swagger UI dynamic import wrapper
│   ├── keys/
│   │   ├── page.tsx          Page shell
│   │   └── KeysClient.tsx    Key management (client component)
│   ├── pricing/
│   │   └── page.tsx          Pricing tier cards
│   └── api/health/
│       └── route.ts          Health check endpoint
├── src/
│   ├── lib/
│   │   └── api-catalog.ts    Typed endpoint + GraphQL query catalog
│   ├── components/
│   │   ├── TopNav.tsx        Navigation bar (client component)
│   │   └── CodeSample.tsx    Multi-language code sample tabs
│   └── __tests__/
│       ├── api-catalog.test.tsx
│       ├── code-sample.test.tsx
│       ├── keys.test.tsx
│       └── nav.test.tsx
├── public/
│   └── openapi.json          OpenAPI 3.0 spec
├── jest.config.ts
├── jest.setup.ts
├── tailwind.config.ts
└── postcss.config.js
```

## Environment variables

| Variable              | Default                 | Purpose                                   |
| --------------------- | ----------------------- | ----------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:3000` | API gateway base URL (used by Swagger UI) |

Copy `.env.example` to `.env.local` and adjust if needed.

## Local development

```bash
# From the monorepo root
pnpm install

# Start the dev server (port 3001)
pnpm --filter @smart-city/developer-portal dev
```

Visit [http://localhost:3001](http://localhost:3001).

## Commands

```bash
# Type check
pnpm --filter @smart-city/developer-portal typecheck

# Lint
pnpm --filter @smart-city/developer-portal lint

# Tests
pnpm --filter @smart-city/developer-portal test

# Production build
pnpm --filter @smart-city/developer-portal build
```

## Notes

- Swagger UI is loaded with `next/dynamic({ ssr: false })` to avoid SSR build failures.
- The API key management UI is a **client-side mock** only — no backend key storage is implemented yet.
- Tailwind v3 is used (not v4) for Next.js 14 compatibility.
- `noUncheckedIndexedAccess: true` is enabled — all array accesses are guarded.
