import { useEffect, useReducer, useRef } from "react";

import {
  initialRunEventState,
  reduceRunEvent,
  runEventSchema,
  type ConnectionState,
  type RunEvent,
  type RunEventState,
} from "./runEventReducer";

type Action =
  | { type: "event"; event: RunEvent }
  | { type: "connection"; connection: ConnectionState }
  | { type: "reset" };

function reducer(state: RunEventState, action: Action): RunEventState {
  if (action.type === "reset") return initialRunEventState;
  if (action.type === "connection") return { ...state, connection: action.connection };
  return reduceRunEvent(state, action.event);
}

export function useRunEvents(runId: string | null, onGap: () => void): RunEventState {
  const [state, dispatch] = useReducer(reducer, initialRunEventState);
  const cursorRef = useRef(0);
  const onGapRef = useRef(onGap);
  onGapRef.current = onGap;

  useEffect(() => {
    cursorRef.current = state.cursor;
    if (state.needsRefetch) onGapRef.current();
  }, [state.cursor, state.needsRefetch]);

  useEffect(() => {
    if (!runId) {
      dispatch({ type: "reset" });
      return;
    }
    dispatch({ type: "connection", connection: "connecting" });
    const source = new EventSource(`/api/v1/runs/${encodeURIComponent(runId)}/events?after=${cursorRef.current}`);
    source.onopen = () => dispatch({ type: "connection", connection: "live" });
    source.onmessage = (message) => {
      try {
        const parsed = runEventSchema.safeParse(JSON.parse(message.data));
        if (parsed.success) dispatch({ type: "event", event: parsed.data });
      } catch {
        dispatch({ type: "connection", connection: "reconnecting" });
      }
    };
    source.onerror = () => dispatch({ type: "connection", connection: "reconnecting" });
    return () => {
      source.close();
      dispatch({ type: "connection", connection: "closed" });
    };
  }, [runId]);

  return state;
}
