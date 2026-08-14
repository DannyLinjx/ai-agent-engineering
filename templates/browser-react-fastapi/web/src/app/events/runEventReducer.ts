import { z } from "zod";

export const runEventSchema = z.object({
  id: z.string().min(1),
  run_id: z.string().min(1),
  sequence: z.number().int().positive(),
  type: z.enum([
    "approval.required",
    "approval.resolved",
    "artifact.created",
    "evidence.added",
    "memory.proposed",
    "memory.rejected",
    "memory.stored",
    "plan.updated",
    "run.status",
    "step.completed",
    "step.failed",
    "step.started",
    "tool.completed",
    "tool.failed",
    "tool.started",
    "verification.completed",
  ]),
  timestamp: z.string().min(1),
  status: z.string().min(1),
  payload: z.record(z.string(), z.unknown()),
});

export type RunEvent = z.infer<typeof runEventSchema>;
export type ConnectionState = "idle" | "connecting" | "live" | "reconnecting" | "closed";

export type RunEventState = {
  cursor: number;
  events: RunEvent[];
  status: string;
  gapDetected: boolean;
  needsRefetch: boolean;
  connection: ConnectionState;
};

export const initialRunEventState: RunEventState = {
  cursor: 0,
  events: [],
  status: "idle",
  gapDetected: false,
  needsRefetch: false,
  connection: "idle",
};

const terminalStatuses = new Set(["completed", "failed", "cancelled"]);

export function reduceRunEvent(state: RunEventState, event: RunEvent): RunEventState {
  if (event.sequence <= state.cursor || state.events.some((item) => item.id === event.id)) return state;
  if (event.sequence !== state.cursor + 1) {
    return { ...state, gapDetected: true, needsRefetch: true };
  }
  const nextStatus = event.type === "run.status" || terminalStatuses.has(event.status) ? event.status : state.status;
  return {
    ...state,
    cursor: event.sequence,
    events: [...state.events, event],
    status: nextStatus,
    gapDetected: false,
    needsRefetch: false,
  };
}
