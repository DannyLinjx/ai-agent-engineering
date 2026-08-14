from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


SAFE_EVENT_TYPES = frozenset(
    {
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
    }
)
BLOCKED_KEY = re.compile(
    r"(?i)(?:api[_-]?key|password|secret|token|credential|environment|\benv\b|reasoning|chain[_-]?of[_-]?thought|hidden|(?:^|_)path$)"
)
SECRET_VALUE = re.compile(r"(?i)(?:\bsk-[a-z0-9_-]{4,}|bearer\s+[a-z0-9._-]+|(?:secret|vault)://[^\s]+)")
ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9_.-])/(?:Users|home|private|etc|var|root|opt)/[^\s]+")


@dataclass(frozen=True)
class BrowserRunEvent:
    id: str
    run_id: str
    sequence: int
    type: str
    timestamp: str
    status: str
    payload: dict[str, Any]


def _sanitize(value: Any, *, depth: int = 0) -> Any:
    if depth >= 6:
        return "[TRUNCATED]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        redacted = SECRET_VALUE.sub("[REDACTED]", value)
        redacted = ABSOLUTE_PATH.sub("[REDACTED_PATH]", redacted)
        return redacted[:1000]
    if isinstance(value, Mapping):
        safe: dict[str, Any] = {}
        for key in sorted(value, key=lambda item: str(item)):
            name = str(key)
            if BLOCKED_KEY.search(name):
                continue
            safe[name] = _sanitize(value[key], depth=depth + 1)
        return safe
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_sanitize(item, depth=depth + 1) for item in list(value)[:50]]
    return str(value)[:1000]


def safe_event(
    event_type: str,
    payload: Mapping[str, Any],
    scope: Mapping[str, str],
    sequence: int,
    *,
    timestamp: datetime | None = None,
) -> BrowserRunEvent:
    if event_type not in SAFE_EVENT_TYPES:
        raise ValueError(f"unsupported browser event: {event_type}")
    run_id = scope.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("browser event scope requires run_id")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("browser event sequence must be a positive integer")
    sanitized = _sanitize(payload)
    if not isinstance(sanitized, dict):
        raise ValueError("browser event payload must be an object")
    status = sanitized.get("status", "updated")
    if not isinstance(status, str) or not status:
        status = "updated"
    occurred_at = timestamp or datetime.now(timezone.utc)
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
    return BrowserRunEvent(
        id=f"{run_id}:{sequence}",
        run_id=run_id,
        sequence=sequence,
        type=event_type,
        timestamp=occurred_at.astimezone(timezone.utc).isoformat(),
        status=status,
        payload=sanitized,
    )
