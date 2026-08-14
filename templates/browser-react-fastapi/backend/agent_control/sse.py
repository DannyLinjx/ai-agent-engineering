from __future__ import annotations

import json

from .auth import Principal
from .db import BrowserDatabase
from .events import BrowserRunEvent


class EventStream:
    def __init__(self, database: BrowserDatabase) -> None:
        self.database = database

    def replay(self, principal: Principal, run_id: str, *, after: int = 0, limit: int = 500) -> list[BrowserRunEvent]:
        run = self.database.connection.execute(
            """SELECT 1 FROM browser_runs
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, run_id),
        ).fetchone()
        if run is None:
            raise KeyError(run_id)
        rows = self.database.connection.execute(
            """SELECT event_json FROM browser_run_events
               WHERE tenant_id = ? AND user_id = ? AND run_id = ? AND sequence > ?
               ORDER BY sequence LIMIT ?""",
            (principal.tenant_id, principal.user_id, run_id, max(0, after), max(1, min(limit, 1000))),
        ).fetchall()
        return [BrowserRunEvent(**json.loads(row["event_json"])) for row in rows]

    @staticmethod
    def encode(event: BrowserRunEvent) -> str:
        data = json.dumps(event.__dict__, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return f"id: {event.sequence}\nevent: {event.type}\ndata: {data}\n\n"

    @staticmethod
    def heartbeat() -> str:
        return ": heartbeat\n\n"
