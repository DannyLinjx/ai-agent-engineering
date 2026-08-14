from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .config import BrowserSettings


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    user_id: str
    role: str
    session_id: str


@dataclass(frozen=True)
class AuthSession:
    principal: Principal
    session_token: str
    csrf_token: str
    expires_at: datetime


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _password_hash(password: str, *, salt: bytes | None = None) -> str:
    if len(password) < 12:
        raise ValueError("password must contain at least 12 characters")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 240_000)
    return "pbkdf2_sha256$240000$" + base64.urlsafe_b64encode(salt).decode("ascii") + "$" + base64.urlsafe_b64encode(digest).decode("ascii")


def _password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_value, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(base64.urlsafe_b64encode(actual).decode("ascii"), expected)
    except (ValueError, TypeError):
        return False


class AuthService:
    def __init__(self, database: object, settings: BrowserSettings) -> None:
        self.database = database
        self.settings = settings

    def create_local_user(self, tenant_id: str, username: str, role: str, password: str) -> None:
        if role not in {"user", "operator", "admin", "auditor"}:
            raise ValueError("invalid role")
        with self.database.connection:
            self.database.connection.execute(
                "INSERT INTO browser_users(tenant_id, username, role, password_hash, active) VALUES (?,?,?,?,1)",
                (tenant_id, username, role, _password_hash(password)),
            )

    def login(self, tenant_id: str, username: str, password: str) -> AuthSession:
        row = self.database.connection.execute(
            "SELECT role, password_hash, active FROM browser_users WHERE tenant_id = ? AND username = ?",
            (tenant_id, username),
        ).fetchone()
        if row is None or not row["active"] or not _password_matches(password, row["password_hash"]):
            raise ValueError("invalid credentials")
        session_token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        session_id = secrets.token_urlsafe(18)
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(seconds=self.settings.session_ttl_seconds)
        principal = Principal(tenant_id, username, row["role"], session_id)
        with self.database.connection:
            self.database.connection.execute(
                """INSERT INTO browser_sessions
                   (token_hash, csrf_hash, tenant_id, user_id, role, session_id, created_at, expires_at, revoked_at)
                   VALUES (?,?,?,?,?,?,?,?,NULL)""",
                (
                    _digest(session_token),
                    _digest(csrf_token),
                    tenant_id,
                    username,
                    row["role"],
                    session_id,
                    created_at.isoformat(),
                    expires_at.isoformat(),
                ),
            )
        return AuthSession(principal, session_token, csrf_token, expires_at)

    def authenticate(self, session_token: str) -> Principal:
        now = datetime.now(timezone.utc).isoformat()
        row = self.database.connection.execute(
            """SELECT tenant_id, user_id, role, session_id FROM browser_sessions
               WHERE token_hash = ? AND revoked_at IS NULL AND expires_at > ?""",
            (_digest(session_token), now),
        ).fetchone()
        if row is None:
            raise PermissionError("authentication required")
        return Principal(row["tenant_id"], row["user_id"], row["role"], row["session_id"])

    def verify_csrf(self, session_token: str, csrf_token: str) -> None:
        row = self.database.connection.execute(
            """SELECT csrf_hash FROM browser_sessions
               WHERE token_hash = ? AND revoked_at IS NULL AND expires_at > ?""",
            (_digest(session_token), datetime.now(timezone.utc).isoformat()),
        ).fetchone()
        if row is None or not hmac.compare_digest(row["csrf_hash"], _digest(csrf_token)):
            raise PermissionError("CSRF validation failed")

    def logout(self, session_token: str) -> None:
        with self.database.connection:
            self.database.connection.execute(
                "UPDATE browser_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
                (datetime.now(timezone.utc).isoformat(), _digest(session_token)),
            )
