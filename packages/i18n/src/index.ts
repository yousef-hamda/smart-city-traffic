/**
 * Shared locale registry for web + mobile.
 *
 * Apps import the catalogs and helpers from here so that adding a locale is a
 * single-package change. RTL handling must use {@link isRtl} — never hardcode
 * direction checks in app code.
 */
import ar from "./catalogs/ar.json";
import en from "./catalogs/en.json";
import he from "./catalogs/he.json";

export const locales = ["en", "he", "ar"] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "en";

export const rtlLocales: readonly Locale[] = ["he", "ar"];

export function isRtl(locale: Locale): boolean {
  return rtlLocales.includes(locale);
}

export type Catalog = typeof en;

export const catalogs: Record<Locale, Catalog> = { en, he, ar };
