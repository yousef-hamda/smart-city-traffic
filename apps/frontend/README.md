# Web Frontend

Next.js 14 (App Router) dashboard with en/he/ar i18n (RTL-aware via
`next-intl`).

> **Phase 1 skeleton.** Implemented now: localized landing page with language
> switcher and correct `dir` flipping, `/api/health`. Landing → full product
> over Phases 10-12 and 17: live Mapbox dashboard, segment drill-down with
> SHAP, 3D digital twin (React Three Fiber), analytics + carbon impact,
> AI assistant chat + voice, scenario simulator, time-travel, admin.

## Environment

| Variable                   | Default                 | Purpose               |
| -------------------------- | ----------------------- | --------------------- |
| `NEXT_PUBLIC_API_URL`      | `http://localhost:8080` | API gateway base URL  |
| `NEXT_PUBLIC_REALTIME_URL` | `http://localhost:8088` | Socket.IO gateway URL |

## Local development

```bash
pnpm install
pnpm --filter @smart-city/frontend dev    # http://localhost:3000
```

## Tests

```bash
pnpm --filter @smart-city/frontend test       # Jest + RTL
pnpm --filter @smart-city/frontend typecheck
```

RTL check: visit `/he` or `/ar` and confirm the layout flips
(`<html dir="rtl">`).
