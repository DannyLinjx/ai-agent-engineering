import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { ApiError, apiRequest } from "./client";

afterEach(() => {
  vi.unstubAllGlobals();
  document.cookie = "agent_csrf=; Max-Age=0; path=/";
});

describe("apiRequest", () => {
  it("rejects a response that violates its schema", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "wrong" }), { status: 200 })));
    await expect(apiRequest("/api/v1/run", z.object({ status: z.literal("ready") }))).rejects.toThrow();
  });

  it("adds CSRF on unsafe requests and preserves correlation errors", async () => {
    document.cookie = "agent_csrf=csrf-value; path=/";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: "conflict", message: "Try again" } }), {
        status: 409,
        headers: { "X-Correlation-ID": "corr-1", "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const failure = apiRequest("/api/v1/run", z.object({ ok: z.boolean() }), { method: "POST" });

    const error = await failure.catch((reason: unknown) => reason);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toEqual(expect.objectContaining({ correlationId: "corr-1", code: "conflict", status: 409 }));
    expect(fetchMock.mock.calls[0][1].headers.get("X-CSRF-Token")).toBe("csrf-value");
  });
});
