from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .auth import Principal


class BrowserDatabase:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA busy_timeout=10000")
        self._migrate()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS browser_users (
                tenant_id TEXT NOT NULL,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (tenant_id, username)
            );
            CREATE TABLE IF NOT EXISTS browser_sessions (
                token_hash TEXT PRIMARY KEY,
                csrf_hash TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                session_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT
            );
            CREATE TABLE IF NOT EXISTS browser_scoped_objects (
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                id TEXT NOT NULL,
                kind TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (tenant_id, user_id, id)
            );
            CREATE INDEX IF NOT EXISTS browser_scoped_object_kind_idx
              ON browser_scoped_objects (tenant_id, user_id, kind, id);
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


class ScopedObjectRepository:
    def __init__(self, database: BrowserDatabase) -> None:
        self.database = database

    def put(self, principal: Principal, object_id: str, kind: str, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_scoped_objects(tenant_id, user_id, id, kind, payload_json)
                   VALUES (?,?,?,?,?)
                   ON CONFLICT(tenant_id, user_id, id) DO UPDATE SET
                     kind = excluded.kind, payload_json = excluded.payload_json""",
                (principal.tenant_id, principal.user_id, object_id, kind, encoded),
            )

    def get(self, principal: Principal, object_id: str) -> dict[str, Any] | None:
        row = self.database.connection.execute(
            """SELECT payload_json FROM browser_scoped_objects
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, object_id),
        ).fetchone()
        return json.loads(row["payload_json"]) if row else None

    def list(self, principal: Principal, kind: str) -> list[dict[str, Any]]:
        rows = self.database.connection.execute(
            """SELECT payload_json FROM browser_scoped_objects
               WHERE tenant_id = ? AND user_id = ? AND kind = ? ORDER BY id""",
            (principal.tenant_id, principal.user_id, kind),
        ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]
