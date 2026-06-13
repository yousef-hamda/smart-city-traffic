import type { Metadata } from "next";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { isRtl, locales } from "../../i18n";
import { Providers } from "@/components/providers";
import "../globals.css";

export const metadata: Metadata = {
  title: "Smart City Traffic",
  description:
    "Smart City Traffic Optimization Platform — real-time traffic monitoring and control.",
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

type LocaleLayoutProps = {
  children: ReactNode;
  params: { locale: string };
};

export default async function LocaleLayout({ children, params: { locale } }: LocaleLayoutProps) {
  if (!(locales as readonly string[]).includes(locale)) {
    notFound();
  }

  // Opt the statically-generated locale routes back into static rendering;
  // next-intl APIs otherwise force dynamic rendering when reading headers.
  setRequestLocale(locale);

  const messages = await getMessages();

  return (
    <html lang={locale} dir={isRtl(locale) ? "rtl" : "ltr"}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Providers>{children}</Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
