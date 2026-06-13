/**
 * i18next setup for the mobile app.
 * Supports en, he, ar with RTL for he/ar via I18nManager.
 */

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { I18nManager } from "react-native";

import en from "./locales/en.json";
import he from "./locales/he.json";
import ar from "./locales/ar.json";

export type SupportedLocale = "en" | "he" | "ar";

const RTL_LOCALES: SupportedLocale[] = ["he", "ar"];

export function isRtl(locale: string): boolean {
  return RTL_LOCALES.includes(locale as SupportedLocale);
}

export function applyRtl(locale: string): void {
  try {
    const shouldRtl = isRtl(locale);
    if (I18nManager.isRTL !== shouldRtl) {
      I18nManager.forceRTL(shouldRtl);
    }
  } catch {
    // I18nManager is a native API — ignore in test environments
  }
}

if (!i18n.isInitialized) {
  void i18n
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
        he: { translation: he },
        ar: { translation: ar },
      },
      lng: "en",
      fallbackLng: "en",
      interpolation: {
        escapeValue: false,
      },
      compatibilityJSON: "v3",
    })
    .then(() => {
      applyRtl(i18n.language);
    });
}

export default i18n;
