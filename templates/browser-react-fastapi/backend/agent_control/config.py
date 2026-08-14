from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrowserSettings:
    database_path: Path
    profile: str = "development"
    auth: str = "local_account"
    host: str = "127.0.0.1"
    scheme: str = "http"
    session_ttl_seconds: int = 3600
    secure_cookies: bool = False

    def __post_init__(self) -> None:
        if self.profile not in {"development", "test", "production"}:
            raise ValueError("invalid Browser profile")
        if self.auth not in {"local_account", "server_session", "oidc"}:
            raise ValueError("Browser control plane requires authentication")
        if self.session_ttl_seconds < 60:
            raise ValueError("session TTL must be at least 60 seconds")
        loopback = self.host in {"127.0.0.1", "::1", "localhost"}
        if self.profile == "production" and self.scheme != "https" and not loopback:
            raise ValueError("production Browser requires HTTPS outside loopback")
