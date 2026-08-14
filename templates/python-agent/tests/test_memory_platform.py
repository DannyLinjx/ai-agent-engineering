from __future__ import annotations

import unittest
from datetime import datetime, timezone

from agent_runtime.memory import MemoryPolicy, MemoryRecord


class MemoryPolicyTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
