from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.auth import Principal
from agent_control.db import BrowserDatabase
from agent_control.runs import RunRepository


class RunRepositoryTests(unittest.TestCase):
    def test_message_run_and_job_are_atomic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            repository = RunRepository(database)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            bob = Principal("tenant-a", "bob", "operator", "session-b")
            conversation_id = repository.create_conversation(alice, "Support request")

            first = repository.send_message(alice, conversation_id, "Investigate request", "idem-1", "browser_chat")
            second = repository.send_message(alice, conversation_id, "Investigate request", "idem-1", "browser_chat")

            self.assertEqual(first.run_id, second.run_id)
            counts = {
                table: database.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("browser_messages", "browser_runs", "browser_jobs")
            }
            self.assertEqual(counts, {"browser_messages": 1, "browser_runs": 1, "browser_jobs": 1})
            with self.assertRaises(KeyError):
                repository.send_message(bob, conversation_id, "Probe", "idem-1", "browser_chat")
            self.assertIsNone(repository.get_run(bob, first.run_id))
            database.close()


if __name__ == "__main__":
    unittest.main()
