import { expect, test } from "@playwright/test";

// Journey 1: land on the dashboard and drill into a segment.
test("dashboard → segment drill-down", async ({ page }) => {
  await page.goto("/en/dashboard");
  // KPI cards + map render (mock data when no backend).
  await expect(page.getByText(/avg speed/i)).toBeVisible();
  // Open a segment from the list/map and see the forecast panel.
  await page.goto("/en/dashboard/segment/jaffa-road-00");
  await expect(page.getByText(/forecast|prediction|SHAP/i)).toBeVisible();
});
