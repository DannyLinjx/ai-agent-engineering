from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.artifacts import ArtifactRepository
from agent_control.auth import Principal
from agent_control.db import BrowserDatabase


class ArtifactRepositoryTests(unittest.TestCase):
    def test_authorized_content_addressed_storage_and_input_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = BrowserDatabase(root / "browser.db")
            repository = ArtifactRepository(database, root / "artifacts", max_artifact_bytes=32, max_user_bytes=40)
            alice = Principal("tenant-a", "alice", "operator", "session-a")
            bob = Principal("tenant-a", "bob", "operator", "session-b")

            artifact = repository.put(alice, "result.txt", "text/plain", b"verified", run_id="run-1")

            self.assertEqual(repository.read(alice, artifact.id), b"verified")
            self.assertNotIn(str(root), str(artifact))
            self.assertIn("attachment", repository.content_disposition(artifact))
            with self.assertRaises(KeyError):
                repository.read(bob, artifact.id)
            with self.assertRaises(ValueError):
                repository.put(alice, "../escape.txt", "text/plain", b"x", run_id="run-1")
            with self.assertRaises(ValueError):
                repository.put(alice, "attack.html", "text/html", b"<script/>", run_id="run-1")
            with self.assertRaises(ValueError):
                repository.put(alice, "large.txt", "text/plain", b"x" * 33, run_id="run-1")
            database.close()


if __name__ == "__main__":
    unittest.main()
