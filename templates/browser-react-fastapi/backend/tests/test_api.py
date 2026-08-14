from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from agent_control.api import create_app
from agent_control.config import BrowserSettings


@dataclass
class FakeMemoryRecord:
    id: str = "memory-1"
    summary: str = "Prefers concise evidence"
    memory_type: str = "preference"
    source: str = "user_statement"
    evidence_refs: tuple[str, ...] = ("message:1",)
    confidence: float = 0.9
    sensitivity: str = "internal"
    status: str = "active"


class FakeMemoryPort:
    def __init__(self) -> None:
        self.deleted = False

    def list(self, scope):
        return [] if self.deleted else [FakeMemoryRecord()]

    def soft_delete(self, scope, record_id):
        self.deleted = record_id == "memory-1"
        return self.deleted

    def export_records(self, scope, format="json"):
        return "[]"


class BrowserApiVerticalSliceTests(unittest.TestCase):
    def test_authenticated_message_run_cancel_and_sse_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(
                BrowserSettings(database_path=Path(tmp) / "browser.db", profile="test"),
                memory_port=FakeMemoryPort(),
            )
            app.state.auth.create_local_user("tenant-a", "alice", "operator", "correct horse battery")
            with TestClient(app) as client:
                login = client.post(
                    "/api/v1/auth/login",
                    json={"tenant_id": "tenant-a", "username": "alice", "password": "correct horse battery"},
                )
                self.assertEqual(login.status_code, 200, login.text)
                csrf = client.cookies.get("agent_csrf")
                self.assertTrue(csrf)
                command_headers = {"X-CSRF-Token": csrf}

                created = client.post(
                    "/api/v1/conversations",
                    json={"title": "Verified incident"},
                    headers=command_headers,
                )
                self.assertEqual(created.status_code, 201, created.text)
                conversation_id = created.json()["id"]
                headers = {**command_headers, "Idempotency-Key": "message-1"}
                sent = client.post(
                    f"/api/v1/conversations/{conversation_id}/messages",
                    json={"text": "Produce a verified incident summary"},
                    headers=headers,
                )
                self.assertEqual(sent.status_code, 202, sent.text)
                run_id = sent.json()["run_id"]
                principal = app.state.auth.authenticate(client.cookies.get("agent_session"))
                approval = app.state.approvals.request(
                    principal, run_id, "write_record", "1", {"record": 42}, "crm:42", "high", ["artifact:1"],
                    datetime.now(timezone.utc) + timedelta(minutes=5),
                )
                artifact = app.state.artifacts.put(
                    principal, "result.json", "application/json", b"{}", run_id=run_id,
                )
                repeated = client.post(
                    f"/api/v1/conversations/{conversation_id}/messages",
                    json={"text": "Produce a verified incident summary"},
                    headers=headers,
                )
                self.assertEqual(repeated.json()["run_id"], run_id)
                self.assertEqual(client.get(f"/api/v1/runs/{run_id}").json()["status"], "queued")

                stream = client.get(f"/api/v1/runs/{run_id}/events?after=0&live=false")
                self.assertEqual(stream.status_code, 200, stream.text)
                self.assertIn('"type":"run.status"', stream.text)
                cancelled = client.post(f"/api/v1/runs/{run_id}/cancel", headers=command_headers)
                self.assertEqual(cancelled.json()["status"], "cancelling")
                listed_approvals = client.get("/api/v1/approvals")
                self.assertEqual(listed_approvals.json()[0]["action_fingerprint"], approval.action_fingerprint)
                decided = client.post(
                    f"/api/v1/approvals/{approval.id}/decision",
                    json={"decision": "rejected"},
                    headers=command_headers,
                )
                self.assertEqual(decided.status_code, 204, decided.text)
                self.assertEqual(client.get("/api/v1/approvals").json(), [])
                self.assertEqual(client.get("/api/v1/artifacts").json()[0]["id"], artifact.id)
                downloaded = client.get(f"/api/v1/artifacts/{artifact.id}/download")
                self.assertEqual(downloaded.content, b"{}")
                self.assertIn("attachment", downloaded.headers["content-disposition"])
                self.assertEqual(client.get("/api/v1/memory").json()[0]["id"], "memory-1")
                self.assertEqual(client.get("/api/v1/memory/export").status_code, 200)
                deleted = client.delete("/api/v1/memory/memory-1", headers=command_headers)
                self.assertEqual(deleted.status_code, 204, deleted.text)
                self.assertEqual(client.get("/api/v1/memory").json(), [])
            app.state.database.close()

    def test_commands_require_csrf_and_unknown_objects_do_not_enumerate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(BrowserSettings(database_path=Path(tmp) / "browser.db", profile="test"))
            app.state.auth.create_local_user("tenant-a", "alice", "operator", "correct horse battery")
            with TestClient(app) as client:
                client.post(
                    "/api/v1/auth/login",
                    json={"tenant_id": "tenant-a", "username": "alice", "password": "correct horse battery"},
                )
                self.assertEqual(
                    client.post("/api/v1/conversations", json={"title": "Denied"}).status_code,
                    403,
                )
                self.assertEqual(client.get("/api/v1/runs/not-a-run").status_code, 404)
                self.assertEqual(client.get("/api/v1/runs/not-a-run/events?live=false").status_code, 404)
            app.state.database.close()


if __name__ == "__main__":
    unittest.main()
