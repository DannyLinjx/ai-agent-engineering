from __future__ import annotations

import unittest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_runtime.memory import (
    MemoryPolicy,
    MemoryQuery,
    MemoryRecord,
    MemoryRetriever,
    MemoryScope,
    SQLiteMemoryStore,
)


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


class MemoryRetrievalTests(RecordFactory, unittest.TestCase):
    def test_fts_retrieval_filters_scope_expiry_and_bounds_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryStore(Path(tmp) / "memory.db")
            as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
            old = as_of - timedelta(days=30)
            store.put(
                self.record(
                    id="strong-old",
                    summary="Project Phoenix launch schedule migration details",
                    content={"project": "Phoenix", "detail": "launch schedule migration"},
                    created_at=old,
                    updated_at=old,
                )
            )
            store.put(self.record(id="weak-new", summary="Project Phoenix", updated_at=as_of, created_at=as_of))
            store.put(self.record(id="unrelated", summary="Unrelated current note", updated_at=as_of, created_at=as_of))
            store.put(self.record(id="expired", summary="Project Phoenix launch schedule", expires_at=as_of - timedelta(seconds=1)))
            store.put(
                self.record(
                    id="bob-private",
                    user_id="bob",
                    summary="Project Phoenix launch schedule",
                )
            )
            retriever = MemoryRetriever(store)

            results = retriever.search(
                MemoryQuery(
                    MemoryScope("tenant-a", "alice"),
                    "project phoenix launch schedule",
                    limit=2,
                    as_of=as_of,
                )
            )

            self.assertEqual([result.record.id for result in results], ["strong-old", "weak-new"])
            self.assertTrue(all(result.record.user_id == "alice" for result in results))
            self.assertTrue(all(result.record.id != "expired" for result in results))
            self.assertIn("keyword_relevance", results[0].score_components)
            store.close()


if __name__ == "__main__":
    unittest.main()
