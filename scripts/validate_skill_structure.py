#!/usr/bin/env python3
"""Validate this AI Agent Engineering Skill package and its internal links."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from _common import emit, issue, iter_files, relative, result

REQUIRED = [
    "SKILL.md", "references/workflow.md", "references/architecture.md",
    "references/agent-factory.md", "references/browser-experience.md", "references/memory-deployment.md",
    "references/agent-runtime.md", "references/tool-system.md", "references/skill-system.md",
    "references/context-management.md", "references/memory-system.md", "references/permission-system.md",
    "references/hook-system.md", "references/subagent-system.md", "references/mcp-integration.md",
    "references/model-routing.md", "references/multi-user-isolation.md", "references/observability.md",
    "references/testing-and-evaluation.md", "references/production-checklist.md", "references/channels-and-integrations.md",
    "scripts/scaffold_agent_project.py", "scripts/validate_agent_architecture.py",
    "scripts/validate_skill_structure.py", "scripts/generate_module_manifest.py",
    "scripts/run_agent_acceptance_tests.py", "scripts/audit_agent_safety.py",
    "scripts/configure_integrations.py", "scripts/validate_integration_config.py",
    "scripts/create_agent_from_blueprint.py", "scripts/plan_memory_deployment.py", "scripts/validate_experience_manifest.py",
    "scripts/validate_memory_manifest.py",
    "templates/typescript-agent/package.json", "templates/python-agent/pyproject.toml",
    "templates/tool-template.ts", "templates/tool-template.py", "templates/permission-policy.yaml",
    "templates/agent-config.yaml", "templates/agent-instructions.md", "templates/integrations.config.json",
    "templates/memory.config.json",
    "templates/tool-manifest.json", "templates/acceptance-test-plan.md",
    "templates/agent-blueprint.json",
    "templates/browser-react-fastapi/overlay-manifest.json", "templates/browser-react-fastapi/README.overlay.md",
    "templates/generic-agent/architecture/module-plan.md", "templates/generic-agent/architecture/memory-adapter-plan.md",
    "templates/generic-agent/tests/contract-test-plan.md",
    "examples/coding-agent.md", "examples/research-agent.md", "examples/enterprise-rag-agent.md",
    "examples/computer-control-agent.md", "examples/multi-agent-workflow.md",
    "assets/architecture-diagram.mmd", "assets/agent-loop.mmd", "assets/permission-flow.mmd", "assets/subagent-flow.mmd",
    "assets/agent-factory-flow.mmd", "assets/browser-control-plane.mmd", "assets/memory-platform.mmd",
    "schemas/agent-config.schema.json", "schemas/agent-state.schema.json", "schemas/tool-manifest.schema.json",
    "schemas/agent-blueprint.schema.json", "schemas/experience-manifest.schema.json",
    "schemas/memory-manifest.schema.json", "schemas/deployment-plan.schema.json", "schemas/browser-run-event.schema.json",
    "schemas/evaluation-case.schema.json", "schemas/trace-event.schema.json", "schemas/production-readiness.schema.json",
    "schemas/integration-config.schema.json", "examples/enterprise-agent-blueprint.json",
    "examples/browser-enterprise-agent-blueprint.json", "examples/local-memory-agent-blueprint.json",
    "examples/memory-deployment-request.json",
    "templates/typescript-agent/src/channels/channel-adapter.ts", "templates/typescript-agent/src/models/provider-registry.ts",
    "templates/python-agent/src/agent_runtime/channels.py", "templates/python-agent/src/agent_runtime/providers.py"
]
OPTIONAL_HOST_ADAPTERS = ("agents/openai.yaml",)
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

def check_frontmatter(path: Path, issues: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        issues.append(issue("frontmatter", "SKILL.md needs YAML frontmatter", path="SKILL.md")); return
    front = text.split("---\n", 2)[1]
    if not re.search(r"(?m)^name:\s*ai-agent-engineering\s*$", front): issues.append(issue("skill-name", "Frontmatter name must be ai-agent-engineering", path="SKILL.md"))
    match = re.search(r"(?ms)^description:\s*(.+?)(?:\n[a-z_]+:|\Z)", front)
    if not match or len(match.group(1).strip()) < 80: issues.append(issue("skill-description", "Description must explain capabilities and trigger conditions", path="SKILL.md"))

def check_links(root: Path, issues: list[dict]) -> None:
    for path in iter_files(root, suffixes={".md"}):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in LINK.findall(text):
            value = target.split("#", 1)[0].strip()
            if not value or "://" in value or value.startswith(("mailto:", "#", "/")): continue
            resolved = (path.parent / value).resolve()
            try: resolved.relative_to(root.resolve())
            except ValueError:
                issues.append(issue("link-escape", f"Link escapes skill root: {target}", path=relative(path, root))); continue
            if not resolved.exists(): issues.append(issue("broken-link", f"Missing link target: {target}", path=relative(path, root)))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.skill.expanduser().resolve()
    issues: list[dict] = []
    for rel in REQUIRED:
        if not (root / rel).is_file(): issues.append(issue("missing-file", "Required file is missing", path=rel))
    if (root / "SKILL.md").is_file(): check_frontmatter(root / "SKILL.md", issues)
    check_links(root, issues)
    json_count = 0
    for path in iter_files(root, suffixes={".json"}):
        json_count += 1
        try: json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc: issues.append(issue("invalid-json", str(exc), path=relative(path, root)))
    jsonl_count = 0
    for path in iter_files(root, suffixes={".jsonl"}):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            jsonl_count += 1
            try: json.loads(line)
            except json.JSONDecodeError as exc: issues.append(issue("invalid-jsonl", str(exc), path=f"{relative(path, root)}:{number}"))
    script_count = 0
    for path in sorted((root / "scripts").glob("*.py")):
        script_count += 1
        try: compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, OSError) as exc: issues.append(issue("python-compile", str(exc), path=relative(path, root)))
        if path.name != "_common.py" and not os.access(path, os.X_OK): issues.append(issue("not-executable", "Script is intended to be invoked with Python", severity="info", path=relative(path, root), hint=f"python {relative(path, root)} --help"))
    host_adapters = {rel: "present" if (root / rel).is_file() else "missing" for rel in OPTIONAL_HOST_ADAPTERS}
    for rel, status in host_adapters.items():
        if status == "missing": issues.append(issue("optional-host-adapter", "Optional host metadata is not installed", severity="warning", path=rel))
    for directory in (root / "agents", root / "host-adapters"):
        if directory.is_dir():
            for path in sorted(item for item in directory.rglob("*") if item.is_file()):
                host_adapters.setdefault(relative(path, root), "present")
    value = result("validate_skill_structure", root, issues, {"required_core_files": len(REQUIRED), "json_files": json_count, "jsonl_records": jsonl_count, "python_scripts": script_count})
    value["core_status"] = value["status"]
    value["optional_host_adapters"] = host_adapters
    value["warnings"] = [item for item in issues if item.get("severity") == "warning"]
    emit(value, json_output=args.json)
    return 1 if value["status"] == "failed" else 0

if __name__ == "__main__": raise SystemExit(main())
