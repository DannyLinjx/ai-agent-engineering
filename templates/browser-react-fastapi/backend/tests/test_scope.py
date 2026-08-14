from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.auth import Principal
from agent_control.db import BrowserDatabase, ScopedObjectRepository


class ScopedRepositoryTests(unittest.TestCase):
    def test_object_access_requires_immutable_principal_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            repository = ScopedObjectRepository(database)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            bob = Principal("tenant-a", "bob", "operator", "session-b")
            other_tenant = Principal("tenant-b", "alice", "operator", "session-c")
            repository.put(alice, "same-shaped-id", "conversation", {"title": "Alice private"})

            self.assertEqual(repository.get(alice, "same-shaped-id")["title"], "Alice private")
            self.assertIsNone(repository.get(bob, "same-shaped-id"))
            self.assertIsNone(repository.get(other_tenant, "same-shaped-id"))
            self.assertEqual(repository.list(bob, "conversation"), [])
            database.close()


if __name__ == "__main__":
    unittest.main()
