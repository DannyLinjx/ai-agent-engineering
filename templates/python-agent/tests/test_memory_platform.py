from __future__ import annotations

import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_runtime.memory import MemoryPolicy, MemoryRecord, MemoryScope, SQLiteMemoryStore


class RecordFactory:
    def record(self, **overrides) -> MemoryRecord:
        values = {
            "id": "mem-1",
            "tenant_id": "tenant-a",
            "user_id": "alice",
            "content": {"preference": "Use concise answers"},
            "summary": "Response preference",
            "memory_type": "preference",
            "source": "user_statement",
            "consent_basis": "explicit",
            "sensitivity": "internal",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        }
        values.update(overrides)
        return MemoryRecord(**values)


class MemoryPolicyTests(RecordFactory, unittest.TestCase):
    def test_policy_rejects_record_without_consent(self) -> None:
        decision = MemoryPolicy().evaluate(self.record(consent_basis="none"))

        self.assertEqual(decision.action, "reject")
        self.assertEqual(decision.reason, "consent_required")

    def test_policy_rejects_secret_material(self) -> None:
        decision = MemoryPolicy().evaluate(self.record(content={"api_key": "sk-test-value"}))

        self.assertEqual(decision.action, "reject")
        self.assertEqual(decision.reason, "secret_material")

    def test_policy_requires_confirmation_for_sensitive_memory(self) -> None:
        decision = MemoryPolicy().evaluate(self.record(sensitivity="sensitive"))

        self.assertEqual(decision.action, "needs_confirmation")


class SQLiteMemoryStoreTests(RecordFactory, unittest.TestCase):
    def test_persistence_and_scope_isolation_survive_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory.db"
            store = SQLiteMemoryStore(path)
            store.put(self.record())
            store.close()

            reopened = SQLiteMemoryStore(path)
            self.assertEqual(reopened.get(MemoryScope("tenant-a", "alice"), "mem-1").summary, "Response preference")
            self.assertIsNone(reopened.get(MemoryScope("tenant-a", "bob"), "mem-1"))
            self.assertIsNone(reopened.get(MemoryScope("tenant-b", "alice"), "mem-1"))
            reopened.close()

    def test_correction_supersedes_without_overwriting_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryStore(Path(tmp) / "memory.db")
            scope = MemoryScope("tenant-a", "alice")
            store.put(self.record())
            corrected = self.record(
                id="mem-2",
                content={"preference": "Use detailed answers"},
                summary="Corrected response preference",
            )

            store.correct(scope, "mem-1", corrected)

            self.assertIsNone(store.get(scope, "mem-1"))
            historical = store.get(scope, "mem-1", include_inactive=True)
            self.assertEqual(historical.status, "superseded")
            self.assertEqual(store.get(scope, "mem-2").supersedes_id, "mem-1")
            store.close()

    def test_expiry_and_soft_delete_emit_pending_index_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryStore(Path(tmp) / "memory.db")
            scope = MemoryScope("tenant-a", "alice")
            now = datetime(2026, 1, 2, tzinfo=timezone.utc)
            store.put(self.record(id="expire", expires_at=now - timedelta(seconds=1)))
            store.put(self.record(id="delete"))

            self.assertEqual(store.expire_due(now), 1)
            self.assertTrue(store.soft_delete(scope, "delete", now=now))
            self.assertIsNone(store.get(scope, "expire"))
            self.assertIsNone(store.get(scope, "delete"))
            event_types = [event["event_type"] for event in store.pending_index_events()]
            self.assertIn("expired", event_types)
            self.assertIn("deleted", event_types)
            store.close()


if __name__ == "__main__":
    unittest.main()
