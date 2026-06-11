import { useLocale, useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";

const languages = [
  { locale: "en", label: "English" },
  { locale: "he", label: "עברית" },
  { locale: "ar", label: "العربية" },
] as const;

export default function HomePage({ params }: { params?: { locale: string } }) {
  // Server-component page: re-affirm the request locale so this route stays
  // statically rendered (mirrors the call in layout.tsx).
  if (params?.locale) {
    setRequestLocale(params.locale);
  }
  const t = useTranslations("home");
  const locale = useLocale();

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "1.5rem",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", fontWeight: 700 }}>{t("title")}</h1>
      <p style={{ fontSize: "1.125rem", color: "#9aa3b5", maxWidth: "40rem" }}>{t("tagline")}</p>

      {/* Placeholder — the full dashboard lands in Phases 10-17 */}
      <a
        href={`/${locale}/dashboard`}
        style={{
          display: "inline-block",
          padding: "0.75rem 1.75rem",
          borderRadius: "0.5rem",
          backgroundColor: "#2563eb",
          color: "#ffffff",
          fontWeight: 600,
        }}
      >
        {t("launchDashboard")}
      </a>

      <nav aria-label={t("language")} style={{ display: "flex", gap: "1rem" }}>
        {languages.map(({ locale: lang, label }) => (
          <a
            key={lang}
            href={`/${lang}`}
            aria-current={lang === locale ? "true" : undefined}
            style={{
              color: lang === locale ? "#ffffff" : "#7dd3fc",
              fontWeight: lang === locale ? 600 : 400,
            }}
          >
            {label}
          </a>
        ))}
      </nav>
    </main>
  );
}
