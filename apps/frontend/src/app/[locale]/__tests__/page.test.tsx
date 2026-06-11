import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";

import en from "@/messages/en.json";
import HomePage from "../page";

function renderHome(locale = "en") {
  return render(
    <NextIntlClientProvider locale={locale} messages={en}>
      <HomePage />
    </NextIntlClientProvider>,
  );
}

describe("HomePage", () => {
  it("renders the localized title and tagline", () => {
    renderHome();
    expect(screen.getByRole("heading", { name: en.home.title })).toBeInTheDocument();
    expect(screen.getByText(en.home.tagline)).toBeInTheDocument();
  });

  it("links the dashboard CTA to the active locale", () => {
    renderHome();
    expect(screen.getByRole("link", { name: en.home.launchDashboard })).toHaveAttribute(
      "href",
      "/en/dashboard",
    );
  });

  it("offers all three locales and marks the active one", () => {
    renderHome();
    const nav = screen.getByRole("navigation", { name: en.home.language });
    expect(nav).toContainElement(screen.getByRole("link", { name: "English" }));
    expect(nav).toContainElement(screen.getByRole("link", { name: "עברית" }));
    expect(nav).toContainElement(screen.getByRole("link", { name: "العربية" }));
    expect(screen.getByRole("link", { name: "English" })).toHaveAttribute("aria-current", "true");
  });
});
