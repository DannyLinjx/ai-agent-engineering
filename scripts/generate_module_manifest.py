#!/usr/bin/env python3
"""Generate a deterministic manifest of an existing agent project."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from _common import iter_files, relative, sha256_file, write_json

MODULE_TERMS = {
    "runtime": ("runtime", "orchestrator", "agent-loop"), "planner": ("planner", "planning"),
    "channels": ("channel", "telegram", "feishu", "lark", "wecom", "slack"),
    "models": ("model", "provider", "router"), "tools": ("tool", "executor", "registry"),
    "permissions": ("permission", "policy", "approval", "guard"), "context": ("context", "compact", "artifact"),
    "memory": ("memory", "retriever", "profile"), "sessions": ("session", "checkpoint", "repository"),
    "skills": ("skill",), "hooks": ("hook",), "subagents": ("subagent", "delegate"), "mcp": ("mcp",),
    "verification": ("verifier", "verification", "eval"), "telemetry": ("telemetry", "trace", "metric", "audit"),
    "storage": ("storage", "database", "migration"), "config": ("config", "schema", "settings")
}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--include-hashes", action="store_true")
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir(): parser.error(f"project is not a directory: {root}")
    files = list(iter_files(root))
    extensions = Counter((p.suffix.lower() or "<none>") for p in files)
    paths = [relative(p, root) for p in files]
    language = "typescript" if any(p.endswith((".ts", ".tsx")) for p in paths) else "python" if any(p.endswith(".py") for p in paths) else "unknown"
    modules = {name: sorted(path for path in paths if any(term in path.lower() for term in terms)) for name, terms in MODULE_TERMS.items()}
    entries = []
    for path, rel in zip(files, paths):
        item = {"path": rel, "bytes": path.stat().st_size}
        if args.include_hashes: item["sha256"] = sha256_file(path)
        entries.append(item)
    manifest = {"version": "1.0", "project": str(root), "language": language, "file_count": len(files), "extensions": dict(sorted(extensions.items())), "modules": modules, "files": entries}
    if args.output: write_json(args.output.expanduser().resolve(), manifest)
    else: print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
