from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_control.auth import Principal
from agent_control.db import BrowserDatabase
from agent_control.runs import RunRepository
from agent_control.worker import WorkerQueue


class WorkerQueueTests(unittest.TestCase):
    def test_lease_owner_token_and_cancellation_are_durable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            runs = RunRepository(database)
            queue = WorkerQueue(database)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            conversation_id = runs.create_conversation(alice, "Work")
            run = runs.send_message(alice, conversation_id, "Do bounded work", "idem-1", "browser_chat")
            now = datetime.now(timezone.utc) + timedelta(seconds=1)

            lease = queue.lease_next("worker-a", now=now, lease_seconds=30)

            self.assertEqual(lease.run_id, run.run_id)
            self.assertFalse(queue.complete(lease.job_id, "worker-b", lease.lease_token, now=now))
            self.assertFalse(queue.complete(lease.job_id, "worker-a", "stale-token", now=now))
            self.assertTrue(queue.heartbeat(lease.job_id, "worker-a", lease.lease_token, now=now + timedelta(seconds=10)))
            runs.request_cancel(alice, run.run_id)
            self.assertTrue(queue.is_cancel_requested(lease))
            self.assertTrue(queue.release(lease.job_id, "worker-a", lease.lease_token, reason="cancelled"))
            database.close()


if __name__ == "__main__":
    unittest.main()
