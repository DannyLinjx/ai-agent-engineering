from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .auth import Principal
from .db import BrowserDatabase


@dataclass(frozen=True)
class JobLease:
    job_id: str
    run_id: str
    principal: Principal
    job_type: str
    payload_json: str
    lease_owner: str
    lease_token: str
    lease_expires_at: str


class WorkerQueue:
    def __init__(self, database: BrowserDatabase) -> None:
        self.database = database

    def lease_next(self, worker_id: str, *, now: datetime | None = None, lease_seconds: int = 30) -> JobLease | None:
        occurred_at = now or datetime.now(timezone.utc)
        expires_at = occurred_at + timedelta(seconds=max(5, lease_seconds))
        row = self.database.connection.execute(
            """SELECT * FROM browser_jobs
               WHERE available_at <= ? AND (
                 status = 'queued' OR (status = 'leased' AND lease_expires_at <= ?)
               ) ORDER BY created_at, id LIMIT 1""",
            (occurred_at.isoformat(), occurred_at.isoformat()),
        ).fetchone()
        if row is None:
            return None
        token = secrets.token_urlsafe(24)
        with self.database.connection:
            cursor = self.database.connection.execute(
                """UPDATE browser_jobs SET status = 'leased', lease_owner = ?, lease_token = ?,
                   lease_expires_at = ?, attempts = attempts + 1, updated_at = ?
                   WHERE id = ? AND (status = 'queued' OR (status = 'leased' AND lease_expires_at <= ?))""",
                (worker_id, token, expires_at.isoformat(), occurred_at.isoformat(), row["id"], occurred_at.isoformat()),
            )
        if not cursor.rowcount:
            return None
        principal = Principal(row["tenant_id"], row["user_id"], row["role"], row["session_id"])
        return JobLease(row["id"], row["run_id"], principal, row["job_type"], row["payload_json"], worker_id, token, expires_at.isoformat())

    def heartbeat(self, job_id: str, owner: str, token: str, *, now: datetime | None = None, lease_seconds: int = 30) -> bool:
        occurred_at = now or datetime.now(timezone.utc)
        expires_at = occurred_at + timedelta(seconds=max(5, lease_seconds))
        with self.database.connection:
            cursor = self.database.connection.execute(
                """UPDATE browser_jobs SET lease_expires_at = ?, updated_at = ?
                   WHERE id = ? AND status = 'leased' AND lease_owner = ? AND lease_token = ?
                     AND lease_expires_at > ?""",
                (expires_at.isoformat(), occurred_at.isoformat(), job_id, owner, token, occurred_at.isoformat()),
            )
        return bool(cursor.rowcount)

    def complete(self, job_id: str, owner: str, token: str, *, now: datetime | None = None) -> bool:
        occurred_at = now or datetime.now(timezone.utc)
        with self.database.connection:
            cursor = self.database.connection.execute(
                """UPDATE browser_jobs SET status = 'completed', updated_at = ?,
                   lease_owner = NULL, lease_token = NULL, lease_expires_at = NULL
                   WHERE id = ? AND status = 'leased' AND lease_owner = ? AND lease_token = ?
                     AND lease_expires_at > ?""",
                (occurred_at.isoformat(), job_id, owner, token, occurred_at.isoformat()),
            )
        return bool(cursor.rowcount)

    def fail(self, job_id: str, owner: str, token: str, *, reason: str, now: datetime | None = None) -> bool:
        return self.release(job_id, owner, token, reason=reason, now=now, failed=True)

    def release(
        self,
        job_id: str,
        owner: str,
        token: str,
        *,
        reason: str,
        now: datetime | None = None,
        failed: bool = False,
    ) -> bool:
        occurred_at = now or datetime.now(timezone.utc)
        status = "failed" if failed else ("cancelled" if reason == "cancelled" else "queued")
        with self.database.connection:
            cursor = self.database.connection.execute(
                """UPDATE browser_jobs SET status = ?, updated_at = ?, available_at = ?,
                   lease_owner = NULL, lease_token = NULL, lease_expires_at = NULL
                   WHERE id = ? AND status = 'leased' AND lease_owner = ? AND lease_token = ?""",
                (status, occurred_at.isoformat(), occurred_at.isoformat(), job_id, owner, token),
            )
        return bool(cursor.rowcount)

    def is_cancel_requested(self, lease: JobLease) -> bool:
        row = self.database.connection.execute(
            """SELECT cancel_requested FROM browser_runs
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (lease.principal.tenant_id, lease.principal.user_id, lease.run_id),
        ).fetchone()
        return bool(row and row["cancel_requested"])
