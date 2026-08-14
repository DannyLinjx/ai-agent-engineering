from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_spa_asset(root: Path, requested_path: str) -> Path:
    static_root = Path(root).resolve()
    if not (static_root / "index.html").is_file():
        raise FileNotFoundError("built Browser index is missing")
    if "\\" in requested_path:
        raise ValueError("invalid static asset path")
    relative = Path(requested_path or "index.html")
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("static asset path escapes root")
    candidate = (static_root / relative).resolve()
    if candidate != static_root and static_root not in candidate.parents:
        raise ValueError("static asset path escapes root")
    if candidate.is_file():
        return candidate
    if relative.parts and relative.parts[0] == "api":
        raise FileNotFoundError(requested_path)
    return static_root / "index.html"


def install_spa_routes(app: Any, root: Path) -> None:
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    static_root = Path(root).resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    def browser_spa(full_path: str) -> FileResponse:
        try:
            asset = resolve_spa_asset(static_root, full_path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid asset path") from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="not found") from exc
        return FileResponse(asset)
