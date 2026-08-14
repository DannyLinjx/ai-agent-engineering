from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.auth import Principal
from agent_control.db import BrowserDatabase
from agent_control.runs import RunRepository
from agent_control.sse import EventStream


class EventStreamTests(unittest.TestCase):
    def test_cursor_replay_is_ordered_deduplicated_and_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            runs = RunRepository(database)
            stream = EventStream(database)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            bob = Principal("tenant-a", "bob", "operator", "session-b")
            conversation_id = runs.create_conversation(alice, "Work")
            run = runs.send_message(alice, conversation_id, "Do work", "idem-1", "browser_chat")
            runs.append_event(alice, run.run_id, "step.started", {"status": "running", "step": "one"})
            runs.append_event(alice, run.run_id, "step.completed", {"status": "completed", "step": "one"})

            events = stream.replay(alice, run.run_id, after=1)

            self.assertEqual([event.sequence for event in events], [2, 3])
            self.assertEqual(len({event.id for event in events}), len(events))
            with self.assertRaises(KeyError):
                stream.replay(bob, run.run_id, after=0)
            self.assertIn(": heartbeat", stream.heartbeat())
            database.close()


if __name__ == "__main__":
    unittest.main()
