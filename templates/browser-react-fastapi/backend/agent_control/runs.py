from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .auth import Principal
from .db import BrowserDatabase
from .events import BrowserRunEvent, safe_event


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RunProjection:
    run_id: str
    conversation_id: str
    status: str
    cancel_requested: bool
    created_at: str
    updated_at: str


class RunRepository:
    def __init__(self, database: BrowserDatabase) -> None:
        self.database = database

    def create_conversation(self, principal: Principal, title: str) -> str:
        if not title.strip() or len(title) > 240:
            raise ValueError("conversation title must be 1-240 characters")
        conversation_id = str(uuid.uuid4())
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_conversations(tenant_id, user_id, id, title, created_at)
                   VALUES (?,?,?,?,?)""",
                (principal.tenant_id, principal.user_id, conversation_id, title.strip(), _now().isoformat()),
            )
        return conversation_id

    def _projection(self, row: object) -> RunProjection:
        return RunProjection(
            run_id=row["id"],
            conversation_id=row["conversation_id"],
            status=row["status"],
            cancel_requested=bool(row["cancel_requested"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_run(self, principal: Principal, run_id: str) -> RunProjection | None:
        row = self.database.connection.execute(
            """SELECT * FROM browser_runs
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, run_id),
        ).fetchone()
        return self._projection(row) if row else None

    def send_message(
        self,
        principal: Principal,
        conversation_id: str,
        text: str,
        idempotency_key: str,
        profile: str,
    ) -> RunProjection:
        if not text.strip() or len(text) > 20_000:
            raise ValueError("message must be 1-20000 characters")
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValueError("invalid idempotency key")
        if profile not in {"browser_chat", "operations_console"}:
            raise ValueError("invalid Browser profile")
        conversation = self.database.connection.execute(
            """SELECT 1 FROM browser_conversations
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, conversation_id),
        ).fetchone()
        if conversation is None:
            raise KeyError(conversation_id)
        existing = self.database.connection.execute(
            """SELECT run_id FROM browser_idempotency
               WHERE tenant_id = ? AND user_id = ? AND idempotency_key = ?""",
            (principal.tenant_id, principal.user_id, idempotency_key),
        ).fetchone()
        if existing:
            projection = self.get_run(principal, existing["run_id"])
            if projection is None:
                raise RuntimeError("idempotency record references a missing Run")
            return projection
        occurred_at = _now()
        message_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_messages
                   (tenant_id, user_id, id, conversation_id, role, text, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (principal.tenant_id, principal.user_id, message_id, conversation_id, "user", text.strip(), occurred_at.isoformat()),
            )
            self.database.connection.execute(
                """INSERT INTO browser_runs
                   (tenant_id, user_id, id, conversation_id, message_id, profile, status,
                    cancel_requested, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,0,?,?)""",
                (
                    principal.tenant_id,
                    principal.user_id,
                    run_id,
                    conversation_id,
                    message_id,
                    profile,
                    "queued",
                    occurred_at.isoformat(),
                    occurred_at.isoformat(),
                ),
            )
            self.database.connection.execute(
                """INSERT INTO browser_jobs
                   (id, tenant_id, user_id, role, session_id, run_id, job_type, status,
                    payload_json, available_at, lease_owner, lease_token, lease_expires_at,
                    attempts, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,'queued',?,?,NULL,NULL,NULL,0,?,?)""",
                (
                    job_id,
                    principal.tenant_id,
                    principal.user_id,
                    principal.role,
                    principal.session_id,
                    run_id,
                    "execute_run",
                    json.dumps({"message_id": message_id}, sort_keys=True, separators=(",", ":")),
                    occurred_at.isoformat(),
                    occurred_at.isoformat(),
                    occurred_at.isoformat(),
                ),
            )
            self.database.connection.execute(
                "INSERT INTO browser_idempotency(tenant_id, user_id, idempotency_key, run_id) VALUES (?,?,?,?)",
                (principal.tenant_id, principal.user_id, idempotency_key, run_id),
            )
            self._append_event_in_transaction(
                principal,
                run_id,
                "run.status",
                {"status": "queued"},
                occurred_at,
            )
        projection = self.get_run(principal, run_id)
        if projection is None:
            raise RuntimeError("Run transaction did not persist")
        return projection

    def _append_event_in_transaction(
        self,
        principal: Principal,
        run_id: str,
        event_type: str,
        payload: Mapping[str, Any],
        occurred_at: datetime,
    ) -> BrowserRunEvent:
        current = self.database.connection.execute(
            """SELECT COALESCE(MAX(sequence), 0) FROM browser_run_events
               WHERE tenant_id = ? AND user_id = ? AND run_id = ?""",
            (principal.tenant_id, principal.user_id, run_id),
        ).fetchone()[0]
        event = safe_event(event_type, payload, {"run_id": run_id}, current + 1, timestamp=occurred_at)
        self.database.connection.execute(
            """INSERT INTO browser_run_events(tenant_id, user_id, run_id, sequence, event_json)
               VALUES (?,?,?,?,?)""",
            (
                principal.tenant_id,
                principal.user_id,
                run_id,
                event.sequence,
                json.dumps(asdict(event), ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            ),
        )
        return event

    def append_event(
        self,
        principal: Principal,
        run_id: str,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> BrowserRunEvent:
        if self.get_run(principal, run_id) is None:
            raise KeyError(run_id)
        with self.database.connection:
            return self._append_event_in_transaction(principal, run_id, event_type, payload, _now())

    def request_cancel(self, principal: Principal, run_id: str) -> RunProjection:
        if self.get_run(principal, run_id) is None:
            raise KeyError(run_id)
        occurred_at = _now()
        with self.database.connection:
            self.database.connection.execute(
                """UPDATE browser_runs SET cancel_requested = 1, status = 'cancelling', updated_at = ?
                   WHERE tenant_id = ? AND user_id = ? AND id = ?""",
                (occurred_at.isoformat(), principal.tenant_id, principal.user_id, run_id),
            )
            self._append_event_in_transaction(principal, run_id, "run.status", {"status": "cancelling"}, occurred_at)
        projection = self.get_run(principal, run_id)
        if projection is None:
            raise RuntimeError("cancelled Run disappeared")
        return projection
