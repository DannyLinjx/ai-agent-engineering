from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .auth import Principal
from .db import BrowserDatabase


def _fingerprint(tool_name: str, tool_version: str, parameters: dict[str, Any], target: str, risk: str) -> str:
    value = {
        "tool_name": tool_name,
        "tool_version": tool_version,
        "parameters": parameters,
        "target": target,
        "risk": risk,
    }
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ApprovalProjection:
    id: str
    run_id: str
    tool_name: str
    tool_version: str
    target: str
    risk: str
    evidence_refs: tuple[str, ...]
    action_fingerprint: str
    expires_at: str
    decision: str


class ApprovalRepository:
    def __init__(self, database: BrowserDatabase) -> None:
        self.database = database

    def request(
        self,
        principal: Principal,
        run_id: str,
        tool_name: str,
        tool_version: str,
        parameters: dict[str, Any],
        target: str,
        risk: str,
        evidence_refs: list[str],
        expires_at: datetime,
    ) -> ApprovalProjection:
        run = self.database.connection.execute(
            "SELECT 1 FROM browser_runs WHERE tenant_id = ? AND user_id = ? AND id = ?",
            (principal.tenant_id, principal.user_id, run_id),
        ).fetchone()
        if run is None:
            raise KeyError(run_id)
        approval_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        fingerprint = _fingerprint(tool_name, tool_version, parameters, target, risk)
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_approvals
                   (tenant_id, user_id, id, run_id, role, session_id, tool_name, tool_version,
                    parameters_json, target, risk, evidence_refs_json, action_fingerprint,
                    expires_at, decision, decision_actor, decided_at, resume_job_id, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending',NULL,NULL,NULL,?)""",
                (
                    principal.tenant_id,
                    principal.user_id,
                    approval_id,
                    run_id,
                    principal.role,
                    principal.session_id,
                    tool_name,
                    tool_version,
                    json.dumps(parameters, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                    target,
                    risk,
                    json.dumps(evidence_refs, ensure_ascii=False, separators=(",", ":")),
                    fingerprint,
                    expires_at.astimezone(timezone.utc).isoformat(),
                    created_at.isoformat(),
                ),
            )
        return ApprovalProjection(
            approval_id,
            run_id,
            tool_name,
            tool_version,
            target,
            risk,
            tuple(evidence_refs),
            fingerprint,
            expires_at.astimezone(timezone.utc).isoformat(),
            "pending",
        )

    def list(self, principal: Principal, *, pending_only: bool = True) -> list[ApprovalProjection]:
        condition = " AND decision = 'pending'" if pending_only else ""
        rows = self.database.connection.execute(
            """SELECT * FROM browser_approvals
               WHERE tenant_id = ? AND user_id = ?""" + condition + " ORDER BY created_at, id",
            (principal.tenant_id, principal.user_id),
        ).fetchall()
        return [
            ApprovalProjection(
                row["id"], row["run_id"], row["tool_name"], row["tool_version"], row["target"], row["risk"],
                tuple(json.loads(row["evidence_refs_json"])), row["action_fingerprint"], row["expires_at"], row["decision"],
            )
            for row in rows
        ]

    def decide(self, principal: Principal, approval_id: str, decision: str, *, now: datetime | None = None) -> None:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        occurred_at = now or datetime.now(timezone.utc)
        with self.database.connection:
            cursor = self.database.connection.execute(
                """UPDATE browser_approvals SET decision = ?, decision_actor = ?, decided_at = ?
                   WHERE tenant_id = ? AND user_id = ? AND id = ? AND decision = 'pending'""",
                (
                    decision,
                    f"{principal.tenant_id}:{principal.user_id}:{principal.session_id}",
                    occurred_at.astimezone(timezone.utc).isoformat(),
                    principal.tenant_id,
                    principal.user_id,
                    approval_id,
                ),
            )
        if not cursor.rowcount:
            raise KeyError(approval_id)

    def resume(
        self,
        principal: Principal,
        approval_id: str,
        tool_name: str,
        tool_version: str,
        parameters: dict[str, Any],
        target: str,
        risk: str,
        *,
        now: datetime | None = None,
    ) -> str:
        occurred_at = now or datetime.now(timezone.utc)
        row = self.database.connection.execute(
            """SELECT * FROM browser_approvals
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, approval_id),
        ).fetchone()
        if row is None:
            raise KeyError(approval_id)
        if row["decision"] != "approved":
            raise PermissionError("approval is not approved")
        if row["expires_at"] <= occurred_at.astimezone(timezone.utc).isoformat():
            raise PermissionError("approval expired")
        actual = _fingerprint(tool_name, tool_version, parameters, target, risk)
        if actual != row["action_fingerprint"]:
            raise PermissionError("approved action changed")
        if row["resume_job_id"]:
            return row["resume_job_id"]
        job_id = str(uuid.uuid4())
        payload = json.dumps({"approval_id": approval_id}, sort_keys=True, separators=(",", ":"))
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_jobs
                   (id, tenant_id, user_id, role, session_id, run_id, job_type, status,
                    payload_json, available_at, lease_owner, lease_token, lease_expires_at,
                    attempts, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,'resume_run','queued',?,?,NULL,NULL,NULL,0,?,?)""",
                (
                    job_id,
                    row["tenant_id"],
                    row["user_id"],
                    row["role"],
                    row["session_id"],
                    row["run_id"],
                    payload,
                    occurred_at.isoformat(),
                    occurred_at.isoformat(),
                    occurred_at.isoformat(),
                ),
            )
            self.database.connection.execute(
                "UPDATE browser_approvals SET resume_job_id = ? WHERE tenant_id = ? AND user_id = ? AND id = ?",
                (job_id, principal.tenant_id, principal.user_id, approval_id),
            )
        return job_id
