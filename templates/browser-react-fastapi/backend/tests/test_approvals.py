from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent_control.approvals import ApprovalRepository
from agent_control.auth import Principal
from agent_control.db import BrowserDatabase
from agent_control.runs import RunRepository
from agent_control.worker import WorkerQueue


class ApprovalRepositoryTests(unittest.TestCase):
    def test_reject_change_expiry_and_scoped_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            runs = RunRepository(database)
            approvals = ApprovalRepository(database)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            conversation_id = runs.create_conversation(alice, "Approval")
            run = runs.send_message(alice, conversation_id, "Need write", "idem-1", "browser_chat")
            now = datetime.now(timezone.utc)
            queue = WorkerQueue(database)
            initial = queue.lease_next("worker-a", now=now + timedelta(milliseconds=1))
            self.assertTrue(queue.complete(initial.job_id, "worker-a", initial.lease_token, now=now + timedelta(seconds=1)))
            rejected = approvals.request(
                alice, run.run_id, "write_record", "1", {"id": "42"}, "crm:42", "high", ["evidence:1"], now + timedelta(minutes=5)
            )
            approvals.decide(alice, rejected.id, "rejected", now=now)
            resume_count = database.connection.execute("SELECT COUNT(*) FROM browser_jobs WHERE job_type = 'resume_run'").fetchone()[0]
            self.assertEqual(resume_count, 0)

            approved = approvals.request(
                alice, run.run_id, "write_record", "1", {"id": "43"}, "crm:43", "high", ["evidence:2"], now + timedelta(minutes=5)
            )
            approvals.decide(alice, approved.id, "approved", now=now)
            with self.assertRaisesRegex(PermissionError, "action changed"):
                approvals.resume(alice, approved.id, "write_record", "1", {"id": "changed"}, "crm:43", "high", now=now)
            job_id = approvals.resume(alice, approved.id, "write_record", "1", {"id": "43"}, "crm:43", "high", now=now)
            lease = queue.lease_next("worker-a", now=now + timedelta(seconds=2))
            self.assertEqual(lease.job_id, job_id)
            self.assertEqual(lease.principal, alice)

            expired = approvals.request(
                alice, run.run_id, "write_record", "1", {"id": "44"}, "crm:44", "high", [], now - timedelta(seconds=1)
            )
            approvals.decide(alice, expired.id, "approved", now=now - timedelta(seconds=2))
            with self.assertRaisesRegex(PermissionError, "expired"):
                approvals.resume(alice, expired.id, "write_record", "1", {"id": "44"}, "crm:44", "high", now=now)
            database.close()


if __name__ == "__main__":
    unittest.main()
