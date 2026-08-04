#!/usr/bin/env python3
"""Copy the TypeScript or Python agent scaffold into a new project directory."""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug: raise ValueError("project name must contain letters or digits")
    return slug

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("typescript", "python"), required=True)
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source = SKILL_ROOT / "templates" / f"{args.language}-agent"
    target = args.target.expanduser().resolve()
    if not source.is_dir():
        print(f"missing scaffold: {source}", file=sys.stderr); return 2
    if target.exists() and any(target.iterdir()):
        print(f"target must be absent or empty: {target}", file=sys.stderr); return 2
    files = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())
    shared = {
        "config/agent-config.yaml": SKILL_ROOT / "templates" / "agent-config.yaml",
        "config/integrations.config.json": SKILL_ROOT / "templates" / "integrations.config.json",
        "config/permission-policy.yaml": SKILL_ROOT / "templates" / "permission-policy.yaml",
        "docs/agent-charter.md": SKILL_ROOT / "templates" / "agent-charter.md",
        "docs/acceptance-test-plan.md": SKILL_ROOT / "templates" / "acceptance-test-plan.md",
    }
    if args.dry_run:
        print("\n".join(sorted(files + list(shared)))); return 0
    target.mkdir(parents=True, exist_ok=True)
    project_slug = slugify(args.name)
    replacements = {"{{PROJECT_NAME}}": args.name, "{{PROJECT_SLUG}}": project_slug, "{{AGENT_ID}}": project_slug, "{{AGENT_NAME}}": args.name}
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
    print(f"created {args.language} agent scaffold at {target} ({len(files) + len(shared)} files)")
    print("next: keep optional integrations disabled/mock or configure config/integrations.config.json, then implement business behavior")
    return 0

if __name__ == "__main__": raise SystemExit(main())
