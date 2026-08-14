from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import MemoryRecord, MemoryScope
from .policy import MemoryPolicy


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class SQLiteMemoryStore:
    def __init__(self, path: Path, *, policy: MemoryPolicy | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.policy = policy or MemoryPolicy()
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA busy_timeout=10000")
        self._migrate()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS memory_schema_meta (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memory_records (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content_json TEXT NOT NULL,
                content_kind TEXT NOT NULL,
                summary TEXT NOT NULL,
                source TEXT NOT NULL,
                evidence_refs_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                importance REAL NOT NULL,
                sensitivity TEXT NOT NULL,
                consent_basis TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT,
                status TEXT NOT NULL,
                conflict_with_ids_json TEXT NOT NULL,
                supersedes_id TEXT,
                embedding_model TEXT,
                embedding_version TEXT
            );
            CREATE INDEX IF NOT EXISTS memory_scope_status_idx
              ON memory_records (tenant_id, user_id, project_id, status, updated_at);
            CREATE TABLE IF NOT EXISTS memory_relations (
                source_id TEXT NOT NULL REFERENCES memory_records(id),
                relation TEXT NOT NULL,
                target_id TEXT NOT NULL REFERENCES memory_records(id),
                PRIMARY KEY (source_id, relation, target_id)
            );
            CREATE TABLE IF NOT EXISTS memory_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                details_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memory_index_outbox (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                applied_at TEXT
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                record_id UNINDEXED,
                tenant_id UNINDEXED,
                user_id UNINDEXED,
                project_id UNINDEXED,
                summary,
                normalized_text,
                tokenize = 'unicode61'
            );
            """
        )
        self.connection.execute(
            "INSERT OR IGNORE INTO memory_schema_meta(version, applied_at) VALUES (?, ?)",
            (1, _iso(datetime.now(timezone.utc))),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "SQLiteMemoryStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _record_values(self, record: MemoryRecord) -> tuple[Any, ...]:
        content_kind = "text" if isinstance(record.content, str) else "object"
        return (
            record.id,
            record.tenant_id,
            record.user_id,
            record.project_id,
            record.memory_type,
            json.dumps(record.content, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            content_kind,
            record.summary,
            record.source,
            json.dumps(record.evidence_refs, separators=(",", ":")),
            record.confidence,
            record.importance,
            record.sensitivity,
            record.consent_basis,
            record.policy_version,
            _iso(record.created_at),
            _iso(record.updated_at),
            _iso(record.expires_at),
            record.status,
            json.dumps(record.conflict_with_ids, separators=(",", ":")),
            record.supersedes_id,
            record.embedding_model,
            record.embedding_version,
        )

    def _insert(self, record: MemoryRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO memory_records (
                id, tenant_id, user_id, project_id, memory_type, content_json,
                content_kind, summary, source, evidence_refs_json, confidence,
                importance, sensitivity, consent_basis, policy_version, created_at,
                updated_at, expires_at, status, conflict_with_ids_json,
                supersedes_id, embedding_model, embedding_version
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            self._record_values(record),
        )

    def _append_event(self, record: MemoryRecord, event_type: str, occurred_at: datetime) -> None:
        scope = (record.tenant_id, record.user_id, record.project_id)
        self.connection.execute(
            """INSERT INTO memory_events
               (record_id, tenant_id, user_id, project_id, event_type, occurred_at, details_json)
               VALUES (?,?,?,?,?,?,?)""",
            (record.id, *scope, event_type, _iso(occurred_at), "{}"),
        )
        self.connection.execute(
            """INSERT INTO memory_index_outbox
               (record_id, tenant_id, user_id, project_id, event_type, created_at, applied_at)
               VALUES (?,?,?,?,?,?,NULL)""",
            (record.id, *scope, event_type, _iso(occurred_at)),
        )

    def _require_accepted(self, record: MemoryRecord) -> None:
        decision = self.policy.evaluate(record)
        if decision.action != "accept":
            raise ValueError(f"memory write rejected by policy: {decision.reason}")

    def put(self, record: MemoryRecord) -> MemoryRecord:
        self._require_accepted(record)
        with self.connection:
            self._insert(record)
            self._append_event(record, "stored", record.updated_at)
        return record

    def _from_row(self, row: sqlite3.Row) -> MemoryRecord:
        content = json.loads(row["content_json"])
        return MemoryRecord(
            id=row["id"],
            tenant_id=row["tenant_id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            memory_type=row["memory_type"],
            content=content,
            summary=row["summary"],
            source=row["source"],
            evidence_refs=tuple(json.loads(row["evidence_refs_json"])),
            confidence=row["confidence"],
            importance=row["importance"],
            sensitivity=row["sensitivity"],
            consent_basis=row["consent_basis"],
            policy_version=row["policy_version"],
            created_at=_datetime(row["created_at"]),
            updated_at=_datetime(row["updated_at"]),
            expires_at=_datetime(row["expires_at"]),
            status=row["status"],
            conflict_with_ids=tuple(json.loads(row["conflict_with_ids_json"])),
            supersedes_id=row["supersedes_id"],
            embedding_model=row["embedding_model"],
            embedding_version=row["embedding_version"],
        )

    def get(self, scope: MemoryScope, record_id: str, *, include_inactive: bool = False) -> MemoryRecord | None:
        status_clause = "" if include_inactive else " AND status = 'active'"
        row = self.connection.execute(
            f"""SELECT * FROM memory_records
                WHERE id = ? AND tenant_id = ? AND user_id = ? AND project_id = ?{status_clause}""",
            (record_id, scope.tenant_id, scope.user_id, scope.project_id),
        ).fetchone()
        return self._from_row(row) if row else None

    def list(self, scope: MemoryScope, *, include_inactive: bool = False) -> list[MemoryRecord]:
        status_clause = "" if include_inactive else " AND status = 'active'"
        rows = self.connection.execute(
            f"""SELECT * FROM memory_records
                WHERE tenant_id = ? AND user_id = ? AND project_id = ?{status_clause}
                ORDER BY created_at, id""",
            (scope.tenant_id, scope.user_id, scope.project_id),
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def correct(self, scope: MemoryScope, record_id: str, replacement: MemoryRecord) -> MemoryRecord:
        original = self.get(scope, record_id)
        if original is None:
            raise KeyError(record_id)
        if replacement.scope != scope or replacement.id == record_id:
            raise ValueError("replacement must have the same scope and a new id")
        replacement = replace(replacement, supersedes_id=record_id, status="active")
        self._require_accepted(replacement)
        with self.connection:
            self.connection.execute(
                """UPDATE memory_records SET status = 'superseded', updated_at = ?
                   WHERE id = ? AND tenant_id = ? AND user_id = ? AND project_id = ? AND status = 'active'""",
                (_iso(replacement.updated_at), record_id, scope.tenant_id, scope.user_id, scope.project_id),
            )
            self._append_event(replace(original, status="superseded"), "superseded", replacement.updated_at)
            self._insert(replacement)
            self.connection.execute(
                "INSERT INTO memory_relations(source_id, relation, target_id) VALUES (?,?,?)",
                (replacement.id, "supersedes", original.id),
            )
            self._append_event(replacement, "stored", replacement.updated_at)
        return replacement

    def soft_delete(self, scope: MemoryScope, record_id: str, *, now: datetime | None = None) -> bool:
        record = self.get(scope, record_id)
        if record is None:
            return False
        occurred_at = now or datetime.now(timezone.utc)
        with self.connection:
            cursor = self.connection.execute(
                """UPDATE memory_records SET status = 'deleted', updated_at = ?
                   WHERE id = ? AND tenant_id = ? AND user_id = ? AND project_id = ? AND status = 'active'""",
                (_iso(occurred_at), record_id, scope.tenant_id, scope.user_id, scope.project_id),
            )
            if cursor.rowcount:
                self._append_event(replace(record, status="deleted"), "deleted", occurred_at)
        return bool(cursor.rowcount)

    def expire_due(self, now: datetime | None = None) -> int:
        occurred_at = now or datetime.now(timezone.utc)
        rows = self.connection.execute(
            "SELECT * FROM memory_records WHERE status = 'active' AND expires_at IS NOT NULL AND expires_at <= ?",
            (_iso(occurred_at),),
        ).fetchall()
        with self.connection:
            for row in rows:
                record = self._from_row(row)
                self.connection.execute(
                    "UPDATE memory_records SET status = 'expired', updated_at = ? WHERE id = ? AND status = 'active'",
                    (_iso(occurred_at), record.id),
                )
                self._append_event(replace(record, status="expired"), "expired", occurred_at)
        return len(rows)

    def pending_index_events(self, *, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """SELECT sequence, record_id, tenant_id, user_id, project_id, event_type, created_at
               FROM memory_index_outbox WHERE applied_at IS NULL ORDER BY sequence LIMIT ?""",
            (max(1, min(limit, 1000)),),
        ).fetchall()
        return [dict(row) for row in rows]

    def mark_index_event_applied(self, sequence: int, *, now: datetime | None = None) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE memory_index_outbox SET applied_at = ? WHERE sequence = ? AND applied_at IS NULL",
                (_iso(now or datetime.now(timezone.utc)), sequence),
            )
        return bool(cursor.rowcount)

    def apply_pending_index_events(self, *, limit: int = 1000) -> int:
        events = self.pending_index_events(limit=limit)
        applied_at = datetime.now(timezone.utc)
        with self.connection:
            for event in events:
                self.connection.execute("DELETE FROM memory_fts WHERE record_id = ?", (event["record_id"],))
                scope = MemoryScope(event["tenant_id"], event["user_id"], event["project_id"])
                record = self.get(scope, event["record_id"], include_inactive=True)
                if event["event_type"] == "stored" and record is not None and record.status == "active":
                    normalized = json.dumps(record.content, ensure_ascii=False, sort_keys=True, default=str)
                    self.connection.execute(
                        """INSERT INTO memory_fts
                           (record_id, tenant_id, user_id, project_id, summary, normalized_text)
                           VALUES (?,?,?,?,?,?)""",
                        (record.id, record.tenant_id, record.user_id, record.project_id, record.summary, normalized),
                    )
                self.connection.execute(
                    "UPDATE memory_index_outbox SET applied_at = ? WHERE sequence = ? AND applied_at IS NULL",
                    (_iso(applied_at), event["sequence"]),
                )
        return len(events)
