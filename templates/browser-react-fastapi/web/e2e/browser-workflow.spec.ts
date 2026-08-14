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

test("authenticated runtime consumes the REST and SSE control-plane contracts", async ({ page }) => {
  let authenticated = false;
  const commandHeaders: string[] = [];
  await page.route("**/api/v1/experience", async (route) => {
    if (!authenticated) {
      await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "authentication required" }) });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ profile: "browser_chat", role: "operator", surfaces: browserChat.surfaces }),
    });
  });
  await page.route("**/api/v1/auth/login", async (route) => {
    authenticated = true;
    await page.context().addCookies([
      { name: "agent_session", value: "session", url: "http://127.0.0.1:4173", httpOnly: true, sameSite: "Strict" },
      { name: "agent_csrf", value: "csrf", url: "http://127.0.0.1:4173", sameSite: "Strict" },
    ]);
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ tenant_id: "tenant-a", user_id: "alice", role: "operator" }) });
  });
  await page.route("**/api/v1/conversations", async (route) => {
    commandHeaders.push(route.request().headers()["x-csrf-token"] ?? "");
    await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ id: "conversation-1", title: "Current request", status: "active" }) });
  });
  await page.route("**/api/v1/conversations/conversation-1/messages", async (route) => {
    commandHeaders.push(route.request().headers()["x-csrf-token"] ?? "");
    expect(route.request().headers()["idempotency-key"]).toBeTruthy();
    await route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({ run_id: "run-1", conversation_id: "conversation-1", status: "queued", cancel_requested: false, created_at: "2026-08-14T00:00:00Z", updated_at: "2026-08-14T00:00:00Z" }),
    });
  });
  await page.route("**/api/v1/runs/run-1/events?after=0", async (route) => {
    const event = { id: "run-1:1", run_id: "run-1", sequence: 1, type: "run.status", timestamp: "2026-08-14T00:00:00Z", status: "queued", payload: { status: "queued" } };
    await route.fulfill({ status: 200, contentType: "text/event-stream", body: `id: 1\ndata: ${JSON.stringify(event)}\n\n` });
  });
  await page.route("**/api/v1/approvals", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{
      id: "approval-1", run_id: "run-1", tool_name: "write_record", tool_version: "1", target: "crm:42",
      risk: "high", evidence_refs: ["artifact:1"], action_fingerprint: "fingerprint-1", expires_at: "2026-08-14T00:05:00Z", decision: "pending",
    }]) });
  });
  await page.route("**/api/v1/approvals/approval-1/decision", async (route) => {
    commandHeaders.push(route.request().headers()["x-csrf-token"] ?? "");
    await route.fulfill({ status: 204 });
  });
  await page.route("**/api/v1/artifacts", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{
      id: "artifact-1", run_id: "run-1", filename: "result.json", media_type: "application/json", size_bytes: 42,
      digest: "012345678901234567890123456789", created_at: "2026-08-14T00:00:00Z",
    }]) });
  });
  await page.route("**/api/v1/memory", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([{
      id: "memory-1", summary: "Prefers concise evidence", memory_type: "preference", source: "user_statement",
      evidence_refs: ["message:1"], confidence: 0.9, sensitivity: "internal", status: "active",
    }]) });
  });
  await page.route("**/api/v1/memory/memory-1", async (route) => {
    commandHeaders.push(route.request().headers()["x-csrf-token"] ?? "");
    await route.fulfill({ status: 204 });
  });

  await page.goto("/conversation");
  await expect(page.getByRole("heading", { name: "Open the Agent desk." })).toBeVisible();
  await page.getByLabel("Tenant").fill("tenant-a");
  await page.getByLabel("Username").fill("alice");
  await page.getByLabel("Password").fill("correct horse battery");
  await page.getByRole("button", { name: "Enter Agent desk" }).click();
  const composer = page.getByLabel("Message Agent");
  await expect(composer).toBeEnabled();
  await composer.fill("Create a governed response");
  await composer.press("Enter");
  await expect(page.getByText("Create a governed response")).toBeVisible();
  await expect(page.getByRole("complementary", { name: "Run inspector" }).getByRole("heading", { name: "queued" })).toBeVisible();
  await page.getByRole("link", { name: /Approvals/ }).click();
  await expect(page.getByText("crm:42")).toBeVisible();
  await page.getByRole("button", { name: "Reject action" }).click();
  await page.getByRole("link", { name: /Artifacts/ }).click();
  await expect(page.getByText("result.json")).toBeVisible();
  await page.getByRole("link", { name: /Memory/ }).click();
  await expect(page.getByText("Prefers concise evidence")).toBeVisible();
  await page.getByRole("button", { name: "Delete Memory" }).click();
  await page.getByRole("button", { name: "Confirm delete" }).click();
  await expect.poll(() => commandHeaders.length).toBe(4);
  expect(commandHeaders.every((value) => value === "csrf")).toBe(true);
});
