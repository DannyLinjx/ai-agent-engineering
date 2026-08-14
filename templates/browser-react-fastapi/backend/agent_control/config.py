from __future__ import annotations

from dataclasses import dataclass
import json
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
    experience_profile: str = "browser_chat"
    surfaces: tuple[str, ...] = ("conversation", "run_inspector", "approvals", "artifacts", "memory")

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
        if self.experience_profile not in {"browser_chat", "operations_console"}:
            raise ValueError("invalid Experience profile")
        allowed_surfaces = {
            "conversation", "run_inspector", "approvals", "artifacts", "memory",
            "overview", "runs", "audit", "models", "capabilities", "settings",
            "access", "health",
        }
        if not self.surfaces or set(self.surfaces) - allowed_surfaces:
            raise ValueError("invalid Experience surfaces")

    @classmethod
    def from_manifest(cls, manifest_path: Path, *, database_path: Path, profile: str = "development") -> "BrowserSettings":
        value = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        return cls(
            database_path=database_path,
            profile=profile,
            auth=value["auth"],
            experience_profile=value["profile"],
            surfaces=tuple(value["generated_surfaces"] or value["planned_surfaces"]),
            secure_cookies=profile == "production",
            scheme="https" if profile == "production" else "http",
        )
