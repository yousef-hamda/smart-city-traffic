import { expect, test } from "@playwright/test";

// Journey 2: the AI assistant surface exposes a voice/ask affordance.
test("assistant voice/ask affordance is present", async ({ page }) => {
  await page.goto("/en/dashboard/segment/jaffa-road-00");
  const askAi = page.getByRole("button", { name: /ask ai|🎤|voice/i });
  await expect(askAi.first()).toBeVisible();
});
