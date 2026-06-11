# Mobile App (Citizen)

React Native (Expo SDK 51) app for residents.

> **Phase 1 skeleton.** Single screen via expo-router. Phase 14 delivers:
> auth against the API gateway, live traffic map with the shared color
> legend, incident reporting (location + type + photo, moderated), push
> notifications for saved routes (Expo Notifications), "best route now",
> offline-tolerant caching, and en/he/ar i18n.

## Environment

| Variable              | Default                 | Purpose              |
| --------------------- | ----------------------- | -------------------- |
| `EXPO_PUBLIC_API_URL` | `http://localhost:8080` | API gateway base URL |

## Local development

```bash
pnpm install
cd apps/mobile
npx expo start          # scan QR with Expo Go, or press i / a for simulators
```

## Tests

```bash
pnpm --filter @smart-city/mobile test   # jest-expo + Testing Library
```
