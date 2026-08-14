import { describe, expect, it } from "vitest";

import { initialRunEventState, reduceRunEvent } from "./runEventReducer";

const event = (sequence: number, status = "running") => ({
  id: `run-1:${sequence}`,
  run_id: "run-1",
  sequence,
  type: "run.status" as const,
  timestamp: "2026-01-01T00:00:00+00:00",
  status,
  payload: { status },
});

describe("reduceRunEvent", () => {
  it("ignores duplicates and projects terminal status", () => {
    const first = reduceRunEvent(initialRunEventState, event(1));
    const duplicate = reduceRunEvent(first, event(1));
    const terminal = reduceRunEvent(duplicate, event(2, "completed"));
    expect(duplicate.events).toHaveLength(1);
    expect(terminal.status).toBe("completed");
    expect(terminal.cursor).toBe(2);
  });

  it("requests a snapshot refetch when an event sequence has a gap", () => {
    const state = reduceRunEvent(reduceRunEvent(initialRunEventState, event(1)), event(3));
    expect(state.gapDetected).toBe(true);
    expect(state.needsRefetch).toBe(true);
    expect(state.cursor).toBe(1);
  });
});
