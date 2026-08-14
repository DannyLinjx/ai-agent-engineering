from __future__ import annotations

import unittest
from dataclasses import dataclass

from agent_control.auth import Principal
from agent_control.memory_api import MemoryProjectionService


@dataclass
class FakeRecord:
    id: str = "mem-1"
    summary: str = "Preferred response style"
    memory_type: str = "preference"
    source: str = "user_statement"
    evidence_refs: tuple[str, ...] = ("message:1",)
    confidence: float = 0.9
    sensitivity: str = "internal"
    status: str = "active"
    content: dict = None


class FakeMemoryPort:
    def __init__(self) -> None:
        self.scopes = []

    def list(self, scope):
        self.scopes.append(scope)
        return [FakeRecord(content={"private": "not projected"})]

    def soft_delete(self, scope, record_id):
        self.scopes.append(scope)
        return record_id == "mem-1"

    def export_records(self, scope, format="json"):
        self.scopes.append(scope)
        return "[]"


class MemoryProjectionServiceTests(unittest.TestCase):
    def test_projection_is_scoped_and_omits_raw_content(self) -> None:
        port = FakeMemoryPort()
        service = MemoryProjectionService(port)
        alice = Principal("tenant-a", "alice", "operator", "session-a")

        projection = service.list(alice)

        self.assertEqual(projection[0]["id"], "mem-1")
        self.assertNotIn("content", projection[0])
        self.assertEqual(port.scopes[0].tenant_id, "tenant-a")
        self.assertEqual(port.scopes[0].user_id, "alice")
        self.assertTrue(service.delete(alice, "mem-1"))
        self.assertEqual(service.export(alice), "[]")


if __name__ == "__main__":
    unittest.main()
