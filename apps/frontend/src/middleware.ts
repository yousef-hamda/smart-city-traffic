import createMiddleware from "next-intl/middleware";
import { defaultLocale, locales } from "./i18n";

export default createMiddleware({
  locales: [...locales],
  defaultLocale,
  localePrefix: "always",
});

export const config = {
  // Match all pathnames except:
  // - /api (API routes such as /api/health must bypass i18n routing)
  // - /_next, /_vercel (framework internals)
  // - paths containing a dot (static files, e.g. favicon.ico)
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
