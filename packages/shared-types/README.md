# @smart-city/shared-types

Domain TypeScript types and Zod runtime schemas shared across the Smart City
Traffic Optimization Platform services.

## Exports

- `SensorReading` + `SensorReadingSchema` (Zod)
- `Incident` + `IncidentSchema` (Zod)
- `VisionEvent`, `Prediction` (with `shapTop5`), `Alert`, `RoadSegment`
  (multilingual `nameEn`/`nameHe`/`nameAr`)
- `UserRole` (`"admin" | "analyst" | "viewer" | "citizen"`)

## Commands

```bash
pnpm --filter @smart-city/shared-types build      # tsc -> dist/ (main + types)
pnpm --filter @smart-city/shared-types test       # Zod round-trip tests
pnpm --filter @smart-city/shared-types lint
pnpm --filter @smart-city/shared-types typecheck
```
