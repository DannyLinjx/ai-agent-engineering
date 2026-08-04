#!/usr/bin/env python3
"""Shared dependency-free helpers for ai-agent-engineering scripts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".artifacts"}

def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def iter_files(root: Path, *, suffixes: set[str] | None = None) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".cache"))
        for name in sorted(files):
            path = Path(current) / name
            if suffixes is None or path.suffix.lower() in suffixes:
                yield path

def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()

def result(tool: str, target: Path, issues: list[dict[str, Any]], details: dict[str, Any] | None = None) -> dict[str, Any]:
    failed = sum(1 for item in issues if item.get("severity") == "error")
    warnings = sum(1 for item in issues if item.get("severity") == "warning")
    return {"tool": tool, "target": str(target.resolve()), "status": "failed" if failed else "passed", "summary": {"errors": failed, "warnings": warnings, "issues": len(issues)}, "issues": issues, "details": details or {}}

def issue(code: str, message: str, *, severity: str = "error", path: str | None = None, hint: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code, "severity": severity, "message": message}
    if path is not None: value["path"] = path
    if hint is not None: value["hint"] = hint
    return value

def emit(value: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    print(f"{value['tool']}: {value['status']} ({value['summary']['errors']} errors, {value['summary']['warnings']} warnings)")
    for item in value["issues"]:
        location = f" [{item['path']}]" if item.get("path") else ""
        print(f"- {item['severity'].upper()} {item['code']}{location}: {item['message']}")
