from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .auth import Principal
from .db import BrowserDatabase


ALLOWED_MEDIA_TYPES = {"text/plain", "application/json", "application/pdf", "image/png", "image/jpeg"}


@dataclass(frozen=True)
class ArtifactProjection:
    id: str
    run_id: str
    filename: str
    media_type: str
    size_bytes: int
    digest: str
    created_at: str


class ArtifactRepository:
    def __init__(
        self,
        database: BrowserDatabase,
        root: Path,
        *,
        max_artifact_bytes: int = 10_000_000,
        max_user_bytes: int = 100_000_000,
    ) -> None:
        self.database = database
        self.root = Path(root).resolve()
        self.objects = self.root / "objects"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.max_artifact_bytes = max_artifact_bytes
        self.max_user_bytes = max_user_bytes

    def put(self, principal: Principal, filename: str, media_type: str, data: bytes, *, run_id: str) -> ArtifactProjection:
        if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
            raise ValueError("artifact filename must not contain a path")
        if media_type not in ALLOWED_MEDIA_TYPES:
            raise ValueError("artifact media type is not allowed")
        if len(data) > self.max_artifact_bytes:
            raise ValueError("artifact exceeds size limit")
        used = self.database.connection.execute(
            "SELECT COALESCE(SUM(size_bytes), 0) FROM browser_artifacts WHERE tenant_id = ? AND user_id = ?",
            (principal.tenant_id, principal.user_id),
        ).fetchone()[0]
        if used + len(data) > self.max_user_bytes:
            raise ValueError("artifact quota exceeded")
        digest = hashlib.sha256(data).hexdigest()
        object_path = (self.objects / digest[:2] / digest).resolve()
        if self.objects not in object_path.parents:
            raise ValueError("artifact path escaped object root")
        object_path.parent.mkdir(parents=True, exist_ok=True)
        created_object = not object_path.exists()
        if created_object:
            object_path.write_bytes(data)
        artifact_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            with self.database.connection:
                self.database.connection.execute(
                    """INSERT INTO browser_artifacts
                       (tenant_id, user_id, id, run_id, filename, media_type, size_bytes, digest, created_at)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (
                        principal.tenant_id,
                        principal.user_id,
                        artifact_id,
                        run_id,
                        filename,
                        media_type,
                        len(data),
                        digest,
                        created_at,
                    ),
                )
        except Exception:
            if created_object and object_path.is_file():
                object_path.unlink()
            raise
        return ArtifactProjection(artifact_id, run_id, filename, media_type, len(data), digest, created_at)

    def metadata(self, principal: Principal, artifact_id: str) -> ArtifactProjection:
        row = self.database.connection.execute(
            """SELECT * FROM browser_artifacts
               WHERE tenant_id = ? AND user_id = ? AND id = ?""",
            (principal.tenant_id, principal.user_id, artifact_id),
        ).fetchone()
        if row is None:
            raise KeyError(artifact_id)
        return ArtifactProjection(row["id"], row["run_id"], row["filename"], row["media_type"], row["size_bytes"], row["digest"], row["created_at"])

    def list(self, principal: Principal) -> list[ArtifactProjection]:
        rows = self.database.connection.execute(
            """SELECT * FROM browser_artifacts
               WHERE tenant_id = ? AND user_id = ? ORDER BY created_at DESC, id""",
            (principal.tenant_id, principal.user_id),
        ).fetchall()
        return [
            ArtifactProjection(row["id"], row["run_id"], row["filename"], row["media_type"], row["size_bytes"], row["digest"], row["created_at"])
            for row in rows
        ]

    def read(self, principal: Principal, artifact_id: str) -> bytes:
        artifact = self.metadata(principal, artifact_id)
        object_path = (self.objects / artifact.digest[:2] / artifact.digest).resolve()
        if self.objects not in object_path.parents or not object_path.is_file():
            raise FileNotFoundError(artifact_id)
        return object_path.read_bytes()

    @staticmethod
    def content_disposition(artifact: ArtifactProjection) -> str:
        safe_name = artifact.filename.replace('"', "_").replace("\r", "_").replace("\n", "_")
        return f'attachment; filename="{safe_name}"'
