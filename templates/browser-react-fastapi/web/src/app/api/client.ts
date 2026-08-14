import type { ZodType } from "zod";
import { z } from "zod";

const errorEnvelope = z.object({
  error: z.object({
    code: z.string().min(1),
    message: z.string().min(1),
  }),
});

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly correlationId: string | null;

  constructor(status: number, code: string, message: string, correlationId: string | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.correlationId = correlationId;
  }
}

function cookie(name: string): string | null {
  const prefix = `${encodeURIComponent(name)}=`;
  for (const part of document.cookie.split(";")) {
    const value = part.trim();
    if (value.startsWith(prefix)) return decodeURIComponent(value.slice(prefix.length));
  }
  return null;
}

export async function apiRequest<T>(path: string, schema: ZodType<T>, init: RequestInit = {}): Promise<T> {
  if (!path.startsWith("/api/")) throw new Error("API path must be same-origin and start with /api/");
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  if (!new Set(["GET", "HEAD", "OPTIONS"]).has(method)) {
    const csrf = cookie("agent_csrf");
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...init, method, headers, credentials: "same-origin" });
  const correlationId = response.headers.get("X-Correlation-ID");
  const text = await response.text();
  const body: unknown = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const parsed = errorEnvelope.safeParse(body);
    throw new ApiError(
      response.status,
      parsed.success ? parsed.data.error.code : "request_failed",
      parsed.success ? parsed.data.error.message : "Request failed",
      correlationId,
    );
  }
  return schema.parse(body);
}
