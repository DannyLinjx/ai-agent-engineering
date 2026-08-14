#!/usr/bin/env python3
"""Copy a runnable reference or language-neutral agent scaffold into a project."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

def available_languages() -> tuple[str, ...]:
    return tuple(sorted(path.name.removesuffix("-agent") for path in (SKILL_ROOT / "templates").glob("*-agent") if path.is_dir()))

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug: raise ValueError("project name must contain letters or digits")
    return slug

def _contained_path(root: Path, relative: str, *, kind: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"invalid overlay {kind}: {relative!r}")
    candidate_rel = Path(relative)
    if candidate_rel.is_absolute() or any(part in {"", ".", ".."} for part in candidate_rel.parts):
        raise ValueError(f"invalid overlay {kind}: {relative!r}")
    resolved_root = root.resolve()
    candidate = (resolved_root / candidate_rel).resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError(f"overlay {kind} escapes its root: {relative}")
    return candidate


def _rendered_bytes(source: Path, replacements: dict[str, str]) -> bytes:
    raw = source.read_bytes()
    try:
        rendered = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered.encode("utf-8")


def _overlay_files(overlays: tuple[str, ...], replacements: dict[str, str]) -> dict[str, tuple[Path, bytes]]:
    collected: dict[str, tuple[Path, bytes]] = {}
    for overlay_name in overlays:
        if not isinstance(overlay_name, str) or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", overlay_name):
            raise ValueError(f"invalid overlay name: {overlay_name!r}")
        overlay_root = SKILL_ROOT / "templates" / overlay_name
        manifest_path = overlay_root / "overlay-manifest.json"
        if not overlay_root.is_dir() or not manifest_path.is_file():
            raise ValueError(f"unknown or incomplete overlay: {overlay_name}")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid overlay manifest: {overlay_name}") from exc
        if not isinstance(manifest, dict) or set(manifest) != {"version", "files"} or manifest["version"] != "1.0" or not isinstance(manifest["files"], list):
            raise ValueError(f"invalid overlay manifest contract: {overlay_name}")
        for entry in manifest["files"]:
            if not isinstance(entry, dict) or set(entry) != {"source", "destination"}:
                raise ValueError(f"invalid overlay file entry: {overlay_name}")
            source = _contained_path(overlay_root, entry["source"], kind="source")
            destination = _contained_path(Path("/overlay-target"), entry["destination"], kind="destination").relative_to("/overlay-target").as_posix()
            if not source.is_file():
                raise ValueError(f"missing overlay source: {overlay_name}/{entry['source']}")
            rendered = _rendered_bytes(source, replacements)
            existing = collected.get(destination)
            if existing and existing[1] != rendered:
                raise ValueError(f"conflicting overlay destination: {destination}")
            collected.setdefault(destination, (source, rendered))
    return collected


def scaffold_project(
    language: str,
    name: str,
    target: Path,
    *,
    dry_run: bool = False,
    overlays: tuple[str, ...] = (),
) -> list[str]:
    if language not in available_languages(): raise ValueError(f"unsupported language: {language}")
    source = SKILL_ROOT / "templates" / f"{language}-agent"
    target = target.expanduser().resolve()
    if not source.is_dir(): raise ValueError(f"missing scaffold: {source}")
    if target.exists() and any(target.iterdir()): raise ValueError(f"target must be absent or empty: {target}")
    files = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())
    shared = {
        "config/agent-config.yaml": SKILL_ROOT / "templates" / "agent-config.yaml",
        "config/agent-instructions.md": SKILL_ROOT / "templates" / "agent-instructions.md",
        "config/integrations.config.json": SKILL_ROOT / "templates" / "integrations.config.json",
        "config/memory.config.json": SKILL_ROOT / "templates" / "memory.config.json",
        "config/permission-policy.yaml": SKILL_ROOT / "templates" / "permission-policy.yaml",
        "config/tool-manifest.json": SKILL_ROOT / "templates" / "tool-manifest.json",
        "docs/agent-charter.md": SKILL_ROOT / "templates" / "agent-charter.md",
        "docs/acceptance-test-plan.md": SKILL_ROOT / "templates" / "acceptance-test-plan.md",
    }
    if language == "generic":
        shared.update({f"schemas/{path.name}": path for path in sorted((SKILL_ROOT / "schemas").glob("*.json"))})
    directory_markers = ["skills/.gitkeep", "data/.gitkeep", ".artifacts/.gitkeep"]
    project_slug = slugify(name)
    replacements = {"{{PROJECT_NAME}}": name, "{{PROJECT_SLUG}}": project_slug, "{{AGENT_ID}}": project_slug, "{{AGENT_NAME}}": name}
    overlay_files = _overlay_files(overlays, replacements)
    occupied = {rel: _rendered_bytes(source / rel, replacements) for rel in files}
    occupied.update({rel: _rendered_bytes(src, replacements) for rel, src in shared.items()})
    occupied.update({rel: b"" for rel in directory_markers})
    for rel, (_, rendered) in overlay_files.items():
        if rel in occupied and occupied[rel] != rendered:
            raise ValueError(f"conflicting overlay destination: {rel}")
        occupied.setdefault(rel, rendered)
    generated = sorted(occupied)
    if dry_run: return generated
    target.mkdir(parents=True, exist_ok=True)
    for rel in files:
        src, dst = source / rel, target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst); continue
        for old, new in replacements.items(): text = text.replace(old, new)
        dst.write_text(text, encoding="utf-8")
    for rel, src in shared.items():
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        for old, new in replacements.items(): text = text.replace(old, new)
        dst.write_text(text, encoding="utf-8")
    for rel in directory_markers:
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.touch()
    for rel, (_, rendered) in overlay_files.items():
        dst = target / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(rendered)
    return generated

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=available_languages(), required=True)
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overlay", action="append", default=[], help="Governed template overlay name; repeatable")
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    try:
        generated = scaffold_project(args.language, args.name, target, dry_run=args.dry_run, overlays=tuple(args.overlay))
    except ValueError as exc:
        print(str(exc), file=sys.stderr); return 2
    if args.dry_run:
        print("\n".join(generated)); return 0
    print(f"created {args.language} agent scaffold at {target} ({len(generated)} files)")
    print("next: keep optional integrations disabled/mock or configure config/integrations.config.json, then implement business behavior")
    return 0

if __name__ == "__main__": raise SystemExit(main())
