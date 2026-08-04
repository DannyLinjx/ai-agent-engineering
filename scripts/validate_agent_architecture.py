#!/usr/bin/env python3
"""Assess whether a project contains the modular foundations of a durable agent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from _common import emit, issue, iter_files, relative, result

CAPABILITIES = {
    "runtime": ("runtime", "orchestrator", "agent_loop", "agent-loop"), "planner": ("planner", "planstep", "plan_step"),
    "channels": ("channeladapter", "channel_adapter", "channels/", "channels\\"),
    "tools": ("toolregistry", "tool_registry", "tools/registry", "tools\\registry"),
    "permissions": ("permissionengine", "permission_engine", "permissions/", "permissions\\"),
    "context": ("contextbuilder", "context_builder", "context/", "context\\"),
    "session_checkpoint": ("checkpoint", "session"), "memory": ("memorymanager", "memory_manager", "memory/", "memory\\"),
    "skills": ("skillloader", "skill_loader", "skills/", "skills\\"), "hooks": ("hookbus", "hook_bus", "hooks/", "hooks\\"),
    "subagents": ("subagent", "delegate"), "mcp": ("mcp",), "model_router": ("modelrouter", "model_router", "models/", "models\\"),
    "verification": ("verifier", "verification"), "observability": ("telemetry", "tracing", "metrics", "audit"),
    "multi_user": ("tenantid", "tenant_id"), "tests": ("tests/", "tests\\", ".test.", "test_")
}
CORE = {"runtime", "tools", "permissions", "context", "session_checkpoint", "verification", "tests"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--min-score", type=float, default=0.60)
    parser.add_argument("--strict", action="store_true", help="Require every capability")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir(): parser.error(f"project is not a directory: {root}")
    candidates = list(iter_files(root, suffixes={".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".yaml", ".yml", ".toml"}))
    corpus_parts: list[str] = []
    for path in candidates:
        rel = relative(path, root)
        corpus_parts.append(rel.lower())
        if path.stat().st_size <= 256000:
            try: corpus_parts.append(path.read_text(encoding="utf-8", errors="ignore").lower())
            except OSError: pass
    corpus = "\n".join(corpus_parts)
    found = {name: any(term.lower() in corpus for term in terms) for name, terms in CAPABILITIES.items()}
    not_applicable: set[str] = set()
    integration_path = root / "config" / "integrations.config.json"
    integration_selection = None
    if integration_path.is_file():
        try:
            integration_selection = json.loads(integration_path.read_text(encoding="utf-8"))
            if integration_selection.get("channels", {}).get("selection") == "none": not_applicable.add("channels")
            if integration_selection.get("mcp", {}).get("selection") == "none": not_applicable.add("mcp")
        except (json.JSONDecodeError, OSError):
            pass
    applicable = [name for name in found if name not in not_applicable]
    score = sum(found[name] for name in applicable) / len(applicable)
    issues = []
    for name, present in found.items():
        if name in not_applicable: continue
        if not present and (args.strict or name in CORE): issues.append(issue("missing-capability", f"No implementation evidence found for {name}", severity="error" if name in CORE else "warning", hint="Add a dedicated module plus focused tests"))
        elif not present: issues.append(issue("missing-capability", f"No implementation evidence found for {name}", severity="warning"))
    if score < args.min_score: issues.append(issue("capability-score", f"Capability score {score:.2f} is below required {args.min_score:.2f}"))
    if not any((root / name).exists() for name in ("package.json", "pyproject.toml")): issues.append(issue("missing-manifest", "Expected package.json or pyproject.toml"))
    value = result("validate_agent_architecture", root, issues, {"score": round(score, 3), "capabilities": found, "not_applicable": sorted(not_applicable), "integration_config": str(integration_path) if integration_path.is_file() else None, "files_scanned": len(candidates)})
    emit(value, json_output=args.json)
    return 1 if value["status"] == "failed" else 0

if __name__ == "__main__": raise SystemExit(main())
