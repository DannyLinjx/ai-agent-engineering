#!/usr/bin/env python3
"""Validate and copy an existing Browser production build without downloading dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ALLOWED_SUFFIXES = {".css", ".js", ".map", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2"}


def _collect(source: Path) -> list[tuple[str, Path]]:
    source = source.resolve()
    index = source / "index.html"
    if not index.is_file() or index.is_symlink():
        raise ValueError("Browser build requires a regular index.html")
    index_text = index.read_text(encoding="utf-8")
    files: list[tuple[str, Path]] = [("index.html", index)]
    assets = source / "assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("Browser build requires an assets directory")
    for path in sorted(item for item in assets.rglob("*") if item.is_file()):
        if path.is_symlink() or path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"undeclared or unsafe Browser asset: {path.name}")
        resolved = path.resolve()
        if source not in resolved.parents:
            raise ValueError("Browser asset escapes source root")
        files.append((resolved.relative_to(source).as_posix(), resolved))
    javascript = [relative for relative, _ in files if relative.endswith(".js")]
    styles = [relative for relative, _ in files if relative.endswith(".css")]
    if not javascript or not styles:
        raise ValueError("Browser build requires at least one JavaScript and one CSS asset")
    if not any(path.name in index_text for _, path in files if path.suffix in {".js", ".css"}):
        raise ValueError("Browser index does not reference its declared assets")
    return files


def sync_assets(source: Path, destination: Path) -> dict:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Browser source and destination must be separate non-nested directories")
    files = _collect(source)
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Browser destination must be absent or empty")
    manifest_files = []
    destination.mkdir(parents=True, exist_ok=True)
    for relative, path in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        manifest_files.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {"version": "1.0", "entry": "index.html", "files": manifest_files}
    (destination / "browser-assets.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Existing Vite dist directory")
    parser.add_argument("--destination", type=Path, required=True, help="Empty Python static asset directory")
    args = parser.parse_args()
    try:
        manifest = sync_assets(args.source, args.destination)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"copied {len(manifest['files'])} validated Browser assets to {args.destination.expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
