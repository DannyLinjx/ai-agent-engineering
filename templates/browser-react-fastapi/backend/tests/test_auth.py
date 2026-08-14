from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_control.auth import AuthService
from agent_control.config import BrowserSettings
from agent_control.db import BrowserDatabase


class AuthServiceTests(unittest.TestCase):
    def test_login_csrf_logout_and_secret_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = BrowserSettings(database_path=Path(tmp) / "browser.db")
            database = BrowserDatabase(settings.database_path)
            auth = AuthService(database, settings)
            auth.create_local_user("tenant-a", "alice", "operator", "correct horse battery staple")

            session = auth.login("tenant-a", "alice", "correct horse battery staple")

            self.assertEqual(auth.authenticate(session.session_token).user_id, "alice")
            auth.verify_csrf(session.session_token, session.csrf_token)
            with self.assertRaises(PermissionError):
                auth.verify_csrf(session.session_token, "wrong")
            stored = database.connection.execute("SELECT token_hash, csrf_hash FROM browser_sessions").fetchone()
            self.assertNotEqual(stored["token_hash"], session.session_token)
            self.assertNotEqual(stored["csrf_hash"], session.csrf_token)
            auth.logout(session.session_token)
            with self.assertRaises(PermissionError):
                auth.authenticate(session.session_token)
            database.close()

    def test_authentication_failures_are_generic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            database = BrowserDatabase(Path(tmp) / "browser.db")
            auth = AuthService(database, BrowserSettings(database_path=Path(tmp) / "browser.db"))
            auth.create_local_user("tenant-a", "alice", "operator", "correct horse battery staple")
            messages = []
            for username, password in (("missing", "wrong"), ("alice", "wrong")):
                with self.assertRaises(ValueError) as caught:
                    auth.login("tenant-a", username, password)
                messages.append(str(caught.exception))
            self.assertEqual(messages, ["invalid credentials", "invalid credentials"])
            database.close()


if __name__ == "__main__":
    unittest.main()
