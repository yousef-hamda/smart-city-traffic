import { expect, test } from "@playwright/test";

// Journey 3: switching English → Hebrew flips the document to RTL.
test("en → he switches to RTL", async ({ page }) => {
  await page.goto("/en");
  await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
  await page.goto("/he");
  await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
});
