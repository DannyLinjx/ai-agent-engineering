import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import type { ExperienceConfig } from "../src/app/shell/AppShell";

const browserChat: ExperienceConfig = {
  projectName: "Field Operations Agent",
  profile: "browser_chat",
  role: "operator",
  surfaces: ["conversation", "run_inspector", "approvals", "artifacts", "memory"],
};

async function selectExperience(page: Page, config: ExperienceConfig) {
  await page.addInitScript((config) => {
    window.__AGENT_EXPERIENCE__ = config;
  }, config);
}

test("chat Run and governance surfaces stay usable across responsive projects", async ({ page }) => {
  await selectExperience(page, browserChat);
  await page.goto("/conversation");
  await expect(page.getByRole("heading", { name: "Agent desk" })).toBeVisible();
  const composer = page.getByLabel("Message Agent");
  await composer.fill("Produce a verified incident summary");
  await composer.press("Enter");
  await expect(page.getByText("Produce a verified incident summary")).toBeVisible();
  await expect(page.getByRole("button", { name: "Stop Run" })).toBeVisible();
  await page.getByRole("button", { name: "Stop Run" }).click();
  await page.getByRole("link", { name: /Approvals/ }).click();
  await expect(page.getByText("No approvals need attention.")).toBeVisible();
  await page.getByRole("link", { name: /Memory/ }).click();
  await expect(page.getByText("No durable Memory stored.")).toBeVisible();
  await expect(page.getByText(/hidden chain of thought/i)).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Created By Deerflow" })).toHaveAttribute("href", "https://deerflow.tech");
});

test("operations navigation is driven by selected surfaces and role", async ({ page }) => {
  await selectExperience(page, {
    projectName: "Operations Agent",
    profile: "operations_console",
    role: "admin",
    surfaces: ["overview", "audit", "models", "capabilities", "settings", "access", "health"],
  });
  await page.goto("/overview");
  await expect(page.getByRole("link", { name: /Overview/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /Settings/ })).toBeVisible();
  await expect(page.getByText("No operational measurements yet.")).toBeVisible();
});
