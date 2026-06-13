// i18n tests — test the i18next instance and locale helpers.
// We import i18n directly (static import) to avoid dynamic-import TS errors.

import i18n, { isRtl, applyRtl } from "../src/i18n/index";

describe("i18n initialization", () => {
  it("initializes with English by default", () => {
    expect(i18n.language).toBe("en");
  });

  it("has English translation for common.appName", () => {
    expect(i18n.t("common.appName")).toBe("Smart City Traffic");
  });

  it("has English translation for auth.login", () => {
    expect(i18n.t("auth.login")).toBe("Log In");
  });

  it("can switch to Hebrew", async () => {
    await i18n.changeLanguage("he");
    expect(i18n.language).toBe("he");
    expect(i18n.t("common.appName")).toBe("תנועה בעיר החכמה");
    // Reset for other tests
    await i18n.changeLanguage("en");
  });

  it("can switch to Arabic", async () => {
    await i18n.changeLanguage("ar");
    expect(i18n.language).toBe("ar");
    expect(i18n.t("common.appName")).toBe("مرور المدينة الذكية");
    // Reset
    await i18n.changeLanguage("en");
  });
});

describe("isRtl", () => {
  it("returns true for Hebrew", () => {
    expect(isRtl("he")).toBe(true);
  });

  it("returns true for Arabic", () => {
    expect(isRtl("ar")).toBe(true);
  });

  it("returns false for English", () => {
    expect(isRtl("en")).toBe(false);
  });
});

describe("applyRtl", () => {
  it("does not throw for any language (native API guarded)", () => {
    expect(() => applyRtl("en")).not.toThrow();
    expect(() => applyRtl("he")).not.toThrow();
    expect(() => applyRtl("ar")).not.toThrow();
  });
});
