#!/usr/bin/env python3
"""Plan or create a governed Agent candidate from an enterprise Blueprint."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from _common import issue, read_json, write_json
from scaffold_agent_project import scaffold_project

SKILL_ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL_KEYS = {
    "version", "blueprint_id", "agent", "product", "perception", "data_governance",
    "capabilities", "autonomy", "service", "implementation", "verification", "assumptions", "unknowns",
}
OPTIONAL_TOP_LEVEL_KEYS = {"experience", "memory", "delivery"}
SECTION_KEYS = {
    "agent": {"id", "name", "owner"},
    "product": {"objective", "intended_users", "business_workflow", "deliverables", "non_goals", "prohibited_uses", "acceptance_criteria"},
    "perception": {"modalities", "intent_fields", "entity_fields", "sources"},
    "data_governance": {"data_classes", "tenant_isolation", "workspace_boundary", "retention_days", "residency", "consent_required", "compliance_constraints"},
    "capabilities": {"required", "optional"},
    "autonomy": {"level", "allowed_actions", "approval_required_actions", "always_denied_actions", "escalation_owner"},
    "service": {"max_steps", "max_tokens", "max_cost_usd", "deadline_seconds", "latency_slo_ms", "availability_target", "quality_threshold", "recovery_target"},
    "implementation": {"language", "profile", "deployment_environment", "optional_integrations"},
    "verification": {"mandatory_scenarios", "deterministic_assertions", "eval_thresholds", "security_gates", "verifier_type"},
}
ENUMS = {
    ("autonomy", "level"): {"assistive", "supervised", "bounded_autonomous"},
    ("implementation", "language"): {"python", "typescript", "generic"},
    ("implementation", "profile"): {"development", "test", "production"},
    ("verification", "verifier_type"): {"deterministic", "hybrid"},
}
PERCEPTION_MODALITIES = {"text", "file", "image", "ocr", "history", "external_event"}
DATA_CLASSES = {"public", "internal", "confidential", "restricted"}
EXPERIENCE_PROFILES = {"headless", "browser_chat", "operations_console"}
REFERENCE_STACKS = {"none", "react_fastapi"}
AUTH_PROFILES = {"none", "local_account", "server_session", "oidc"}
REALTIME_PROFILES = {"none", "sse", "websocket"}
MEMORY_PROFILES = {"local", "hybrid", "enterprise"}
DELIVERY_ENGAGEMENTS = {"plan_only", "guided_install", "end_to_end"}
PROFILE_SECTION_KEYS = {
    "experience": {"profile", "reference_stack", "auth", "realtime", "surfaces"},
    "memory": {"enabled", "profile", "canonical_store", "keyword_index", "vector_index", "graph_store", "framework"},
    "delivery": {"engagement"},
}
BROWSER_CHAT_CAPABILITIES = {
    "browser-experience", "session", "checkpoint", "security", "permissions", "verification",
}
OPERATIONS_CONSOLE_CAPABILITIES = BROWSER_CHAT_CAPABILITIES | {
    "observability", "operations", "multi-user-isolation", "audit-and-artifacts", "realtime-events",
}
MEMORY_CAPABILITIES = {"memory", "session", "checkpoint", "memory-governance"}
ENTERPRISE_MEMORY_CAPABILITIES = MEMORY_CAPABILITIES | {
    "operations", "multi-user-isolation", "memory-migration", "backup-and-recovery",
}
PHASE_BY_CAPABILITY = {
    "permissions": "P0", "security": "P0", "runtime": "P1", "planner": "P1", "tools": "P2",
    "session": "P3", "checkpoint": "P3", "context": "P4", "memory": "P5", "skills": "P6",
    "hooks": "P6", "channels": "P7", "subagents": "P7", "mcp": "P7", "verification": "P8",
    "evaluation": "P8", "model-providers": "P9", "model-routing": "P9", "observability": "P10",
    "multi-user-isolation": "P10", "operations": "P10",
    "browser-experience": "P8", "realtime-events": "P3", "memory-governance": "P5",
    "audit-and-artifacts": "P8", "memory-migration": "P10", "backup-and-recovery": "P10",
}
SCAFFOLD_CAPABILITIES = {
    "runtime", "planner", "tools", "skills", "context", "session", "checkpoint", "memory", "permissions",
    "hooks", "channels", "subagents", "mcp", "model-providers", "model-routing", "verification", "observability",
    "multi-user-isolation", "security", "evaluation", "operations",
}
APPROVAL_TRIGGERS = {"external_write", "production_change", "production_release", "sensitive_data_access", "scope_expansion"}
CREDENTIAL_KEY = re.compile(r"(?i)^(?:api[_-]?key|password|secret|access[_-]?token|auth[_-]?token|credential|credentials|credential_refs)$")
CREDENTIAL_VALUE = re.compile(r"(?i)^(?:sk-|secret://|env://|vault://|bearer\s+|raw-secret)")
SAFE_BROWSER_EVENTS = (
    "approval.required", "approval.resolved", "artifact.created", "evidence.added",
    "memory.proposed", "memory.rejected", "memory.stored", "plan.updated",
    "run.status", "step.completed", "step.failed", "step.started", "tool.completed",
    "tool.failed", "tool.started", "verification.completed",
)
BROWSER_CHAT_SURFACES = {"conversation", "run_inspector", "approvals", "artifacts", "memory"}
OPERATIONS_SURFACES = BROWSER_CHAT_SURFACES | {
    "overview", "runs", "audit", "models", "capabilities", "settings", "access", "health",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_blueprint(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValueError("Blueprint must be a JSON object")
    return value


def normalize_profiles(value: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(value)
    experience = value.get("experience") if isinstance(value.get("experience"), dict) else {}
    memory = value.get("memory") if isinstance(value.get("memory"), dict) else {}
    delivery = value.get("delivery") if isinstance(value.get("delivery"), dict) else {}
    normalized["experience"] = {
        "profile": "headless",
        "reference_stack": "none",
        "auth": "none",
        "realtime": "none",
        "surfaces": [],
        **experience,
    }
    normalized["memory"] = {
        "enabled": False,
        "profile": "local",
        "canonical_store": "sqlite",
        "keyword_index": "sqlite_fts5",
        "vector_index": "none",
        "graph_store": "none",
        "framework": "native",
        **memory,
    }
    normalized["delivery"] = {"engagement": "plan_only", **delivery}
    return normalized


def derive_profile_capabilities(value: dict[str, Any]) -> set[str]:
    normalized = normalize_profiles(value)
    experience_profile = normalized["experience"].get("profile")
    memory = normalized["memory"]
    derived: set[str] = set()
    if experience_profile == "browser_chat":
        derived.update(BROWSER_CHAT_CAPABILITIES)
    elif experience_profile == "operations_console":
        derived.update(OPERATIONS_CONSOLE_CAPABILITIES)
    if memory.get("enabled"):
        if memory.get("profile") == "enterprise":
            derived.update(ENTERPRISE_MEMORY_CAPABILITIES)
        else:
            derived.update(MEMORY_CAPABILITIES)
    return derived


def _section(value: dict[str, Any], name: str) -> dict[str, Any]:
    child = value.get(name)
    return child if isinstance(child, dict) else {}


def _string_set(value: Any) -> set[str]:
    return {item for item in value if isinstance(item, str)} if isinstance(value, list) else set()


def _inline_credentials(value: Any, path: str = "") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if CREDENTIAL_KEY.search(key):
                findings.append(issue("inline-credential", "Credential-like fields are forbidden in Agent Blueprints", path=child_path))
            findings.extend(_inline_credentials(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_inline_credentials(child, f"{path}[{index}]"))
    elif isinstance(value, str) and CREDENTIAL_VALUE.search(value):
        findings.append(issue("inline-credential", "Credential-like values are forbidden in Agent Blueprints", path=path))
    return findings


def _approval_trigger(action: str) -> str | None:
    if "外部" in action and any(marker in action for marker in ("写", "发送", "发布", "提交")):
        return "external_write"
    normalized = re.sub(r"[^a-z0-9]+", "_", action.lower()).strip("_")
    if normalized in APPROVAL_TRIGGERS:
        return normalized
    words = set(normalized.split("_"))
    if "external" in words and ({"write", "send", "publish", "post"} & words):
        return "external_write"
    return None


def _validate_profile_sections(value: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for section, allowed_keys in PROFILE_SECTION_KEYS.items():
        child = value.get(section)
        if child is None:
            continue
        if not isinstance(child, dict):
            findings.append(issue("invalid-type", "Profile section must be an object", path=section))
            continue
        for key in sorted(set(child) - allowed_keys):
            findings.append(issue("unknown-field", "Unknown profile field", path=f"{section}.{key}"))

    normalized = normalize_profiles(value)
    experience = normalized["experience"]
    memory = normalized["memory"]
    delivery = normalized["delivery"]
    enum_fields = (
        ("experience.profile", experience.get("profile"), EXPERIENCE_PROFILES),
        ("experience.reference_stack", experience.get("reference_stack"), REFERENCE_STACKS),
        ("experience.auth", experience.get("auth"), AUTH_PROFILES),
        ("experience.realtime", experience.get("realtime"), REALTIME_PROFILES),
        ("memory.profile", memory.get("profile"), MEMORY_PROFILES),
        ("memory.canonical_store", memory.get("canonical_store"), {"sqlite", "postgresql"}),
        ("memory.keyword_index", memory.get("keyword_index"), {"none", "sqlite_fts5", "postgres_fts"}),
        ("memory.vector_index", memory.get("vector_index"), {"none", "pgvector", "redis", "qdrant", "milvus", "weaviate", "mem0"}),
        ("memory.graph_store", memory.get("graph_store"), {"none", "neo4j", "mem0"}),
        ("memory.framework", memory.get("framework"), {"native", "mem0"}),
        ("delivery.engagement", delivery.get("engagement"), DELIVERY_ENGAGEMENTS),
    )
    for path, actual, allowed in enum_fields:
        if actual not in allowed:
            findings.append(issue("invalid-enum", f"Expected one of {sorted(allowed)}", path=path))

    surfaces = experience.get("surfaces")
    if not isinstance(surfaces, list) or not all(isinstance(item, str) and item for item in surfaces):
        findings.append(issue("invalid-list", "Experience surfaces must be a list of non-empty strings", path="experience.surfaces"))
    elif len(surfaces) != len(set(surfaces)):
        findings.append(issue("duplicate-item", "Experience surfaces must be unique", path="experience.surfaces"))
    if not isinstance(memory.get("enabled"), bool):
        findings.append(issue("invalid-type", "Memory enabled must be a boolean", path="memory.enabled"))

    experience_profile = experience.get("profile")
    if experience_profile in {"browser_chat", "operations_console"}:
        if experience.get("reference_stack") == "none":
            findings.append(issue("experience-stack-required", "Browser profiles require a reference stack", path="experience.reference_stack"))
        if experience.get("auth") == "none":
            findings.append(issue("experience-auth-required", "Browser profiles require authenticated identity", path="experience.auth"))
        if experience.get("realtime") == "none":
            findings.append(issue("experience-realtime-required", "Browser profiles require a realtime observation transport", path="experience.realtime"))
    elif experience_profile == "headless":
        if experience.get("reference_stack") != "none" or experience.get("auth") != "none" or experience.get("realtime") != "none" or surfaces:
            findings.append(issue("headless-profile-conflict", "Headless profile cannot declare browser components", path="experience"))

    if memory.get("enabled"):
        memory_profile = memory.get("profile")
        canonical_store = memory.get("canonical_store")
        if memory_profile in {"hybrid", "enterprise"} and canonical_store != "postgresql":
            findings.append(issue("enterprise-canonical-store", "Hybrid and enterprise Memory require PostgreSQL as canonical store", path="memory.canonical_store"))
        if memory_profile == "local" and canonical_store != "sqlite":
            findings.append(issue("local-canonical-store", "Local Memory requires SQLite as canonical store", path="memory.canonical_store"))
        if memory.get("vector_index") == "pgvector" and canonical_store != "postgresql":
            findings.append(issue("pgvector-store-required", "pgvector requires PostgreSQL canonical storage", path="memory.vector_index"))
        if memory.get("graph_store") == "neo4j":
            scenarios = _string_set(_section(value, "verification").get("mandatory_scenarios"))
            graph_terms = ("graph", "relationship", "multi-hop", "图", "关系", "多跳")
            if not any(any(term in scenario.lower() for term in graph_terms) for scenario in scenarios):
                findings.append(issue("graph-acceptance-required", "Neo4j requires an explicit graph acceptance scenario", path="memory.graph_store"))
    return findings


def validate_blueprint(value: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    missing = sorted(TOP_LEVEL_KEYS - set(value))
    unexpected = sorted(set(value) - TOP_LEVEL_KEYS - OPTIONAL_TOP_LEVEL_KEYS)
    for key in missing:
        issues.append(issue("missing-field", "Required Blueprint field is missing", path=key))
    for key in unexpected:
        issues.append(issue("unknown-field", "Unknown Blueprint field", path=key))
    for section, keys in SECTION_KEYS.items():
        child = value.get(section)
        if not isinstance(child, dict):
            issues.append(issue("invalid-type", "Blueprint section must be an object", path=section))
            continue
        for key in sorted(keys - set(child)):
            issues.append(issue("missing-field", "Required section field is missing", path=f"{section}.{key}"))
        for key in sorted(set(child) - keys):
            issues.append(issue("unknown-field", "Unknown section field", path=f"{section}.{key}"))
    for (section, field), allowed in ENUMS.items():
        child = value.get(section)
        actual = child.get(field) if isinstance(child, dict) else None
        if actual not in allowed:
            issues.append(issue("invalid-enum", f"Expected one of {sorted(allowed)}", path=f"{section}.{field}"))
    for section, field in (
        ("agent", "id"), ("agent", "name"), ("agent", "owner"), ("product", "objective"),
        ("data_governance", "workspace_boundary"), ("data_governance", "residency"),
        ("autonomy", "escalation_owner"), ("service", "recovery_target"),
        ("implementation", "deployment_environment"),
    ):
        child = value.get(section)
        actual = child.get(field) if isinstance(child, dict) else None
        if not isinstance(actual, str) or not actual.strip():
            issues.append(issue("invalid-string", "Expected a non-empty string", path=f"{section}.{field}"))
    for section, field in (
        ("product", "intended_users"), ("product", "business_workflow"), ("product", "deliverables"),
        ("product", "acceptance_criteria"), ("perception", "modalities"), ("perception", "intent_fields"),
        ("perception", "sources"), ("capabilities", "required"), ("autonomy", "allowed_actions"),
        ("autonomy", "always_denied_actions"), ("verification", "mandatory_scenarios"),
        ("verification", "deterministic_assertions"), ("verification", "security_gates"),
    ):
        child = value.get(section)
        actual = child.get(field) if isinstance(child, dict) else None
        if not isinstance(actual, list) or not actual or not all(isinstance(item, str) and item.strip() for item in actual):
            issues.append(issue("invalid-list", "Expected a non-empty list of strings", path=f"{section}.{field}"))
    perception = value.get("perception", {})
    if isinstance(perception, dict) and isinstance(perception.get("modalities"), list):
        for index, modality in enumerate(perception["modalities"]):
            if modality not in PERCEPTION_MODALITIES:
                issues.append(issue("invalid-enum", f"Expected one of {sorted(PERCEPTION_MODALITIES)}", path=f"perception.modalities[{index}]"))
    governance = value.get("data_governance", {})
    if isinstance(governance, dict):
        data_classes = governance.get("data_classes")
        if not isinstance(data_classes, list) or not data_classes:
            issues.append(issue("invalid-list", "Expected a non-empty list of data classes", path="data_governance.data_classes"))
        else:
            for index, data_class in enumerate(data_classes):
                if data_class not in DATA_CLASSES:
                    issues.append(issue("invalid-enum", f"Expected one of {sorted(DATA_CLASSES)}", path=f"data_governance.data_classes[{index}]"))
        for field in ("tenant_isolation", "consent_required"):
            if not isinstance(governance.get(field), bool):
                issues.append(issue("invalid-type", "Expected a boolean", path=f"data_governance.{field}"))
        retention = governance.get("retention_days")
        if not isinstance(retention, int) or isinstance(retention, bool) or retention < 0:
            issues.append(issue("invalid-retention", "Expected a non-negative integer", path="data_governance.retention_days"))
    service = value.get("service", {})
    if isinstance(service, dict):
        for field in ("max_steps", "max_tokens", "deadline_seconds", "latency_slo_ms"):
            actual = service.get(field)
            if not isinstance(actual, int) or isinstance(actual, bool) or actual < 1:
                issues.append(issue("invalid-budget", "Expected a positive integer", path=f"service.{field}"))
        cost = service.get("max_cost_usd")
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
            issues.append(issue("invalid-budget", "Expected a non-negative number", path="service.max_cost_usd"))
        for field in ("availability_target", "quality_threshold"):
            actual = service.get(field)
            if not isinstance(actual, (int, float)) or isinstance(actual, bool) or not 0 <= actual <= 1:
                issues.append(issue("invalid-threshold", "Expected a number from 0 to 1", path=f"service.{field}"))
    integrations = value.get("implementation", {}).get("optional_integrations") if isinstance(value.get("implementation"), dict) else None
    if not isinstance(integrations, dict) or set(integrations) != {"channels", "model_provider", "mcp"}:
        issues.append(issue("invalid-integrations", "Optional integrations must declare channels, model_provider, and mcp", path="implementation.optional_integrations"))
    else:
        choices = {"channels": {"none", "configured"}, "model_provider": {"mock", "none", "auto", "configured"}, "mcp": {"none", "configured"}}
        for name, allowed in choices.items():
            if integrations.get(name) not in allowed:
                issues.append(issue("invalid-enum", f"Expected one of {sorted(allowed)}", path=f"implementation.optional_integrations.{name}"))
    for list_name in ("assumptions", "unknowns"):
        items = value.get(list_name)
        if not isinstance(items, list):
            issues.append(issue("invalid-type", "Expected an array", path=list_name))
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict) or set(item) != {"id", "statement", "risk", "resolution"}:
                issues.append(issue("invalid-decision-item", "Decision item needs id, statement, risk, and resolution", path=f"{list_name}[{index}]"))
                continue
            if item["risk"] not in {"low", "medium", "high", "critical"} or item["resolution"] not in {"assumed", "resolved", "open"}:
                issues.append(issue("invalid-decision-item", "Invalid risk or resolution", path=f"{list_name}[{index}]"))
    issues.extend(_inline_credentials(value))
    issues.extend(_validate_profile_sections(value))
    return issues


def build_recipe(value: dict[str, Any]) -> dict[str, Any]:
    catalog = read_json(SKILL_ROOT / "assets" / "capability-catalog.json")
    known = set(catalog["capabilities"])
    capabilities = _section(value, "capabilities")
    declared_required = _string_set(capabilities.get("required"))
    derived_required = derive_profile_capabilities(value)
    required = declared_required | derived_required
    optional = _string_set(capabilities.get("optional"))
    blockers: list[dict[str, Any]] = validate_blueprint(value)
    for capability in sorted(required - known):
        blockers.append(issue("unknown-capability", "Required capability is not in the capability catalog", path=f"capabilities.required:{capability}"))
    unknowns = value.get("unknowns") if isinstance(value.get("unknowns"), list) else []
    for item in unknowns:
        if isinstance(item, dict) and item.get("resolution") == "open" and item.get("risk") in {"high", "critical"}:
            blockers.append(issue("material-unknown", item.get("statement", "Material unknown remains open"), path=f"unknowns:{item.get('id', 'unknown')}"))
    selected = sorted(required & known & SCAFFOLD_CAPABILITIES)
    planned = sorted((required & known) - set(selected))
    optional_not_applicable = sorted(optional - required)
    blocked_capabilities = sorted(required - known)
    autonomy = _section(value, "autonomy")
    implementation = _section(value, "implementation")
    experience = normalize_profiles(value)["experience"]
    governance = _section(value, "data_governance")
    approvals = _string_set(autonomy.get("approval_required_actions"))
    profile = implementation.get("profile", "development")
    data_classes = _string_set(governance.get("data_classes"))
    if profile == "production":
        approvals.add("production_release")
    if data_classes & {"confidential", "restricted"}:
        approvals.add("sensitive_data_access")
    allowed_actions = _string_set(autonomy.get("allowed_actions"))
    for action in sorted(allowed_actions):
        trigger = _approval_trigger(action)
        if trigger and trigger not in approvals:
            blockers.append(issue("approval-required", f"{trigger} must require human approval", path="autonomy.approval_required_actions"))
    phases = {"P0", "P8"}
    phases.update(PHASE_BY_CAPABILITY[item] for item in required if item in PHASE_BY_CAPABILITY)
    if profile == "production":
        phases.add("P10")
    generated_files = [
        "factory/agent-blueprint.json", "factory/build-recipe.json", "factory/capability-matrix.json",
        "factory/assembly-manifest.json", "factory/release-checklist.json",
        "factory/experience-manifest.json", "factory/memory-manifest.json", "factory/deployment-plan.json",
        "config/experience.config.json",
    ]
    overlays: list[str] = []
    if (
        implementation.get("language") == "python"
        and experience["profile"] != "headless"
        and experience["reference_stack"] == "react_fastapi"
    ):
        overlays.append("browser-react-fastapi")
    recipe: dict[str, Any] = {
        "version": "1.0",
        "blueprint_id": value.get("blueprint_id", "invalid"),
        "blueprint_hash": content_hash(value),
        "status": "blocked" if blockers else "planned",
        "scaffold": implementation.get("language", "generic"),
        "overlays": overlays,
        "profile": profile,
        "derived_required": sorted(derived_required),
        "applicable_phases": sorted(phases, key=lambda item: int(item[1:])),
        "capabilities": {
            "selected": selected,
            "planned": planned,
            "blocked": blocked_capabilities,
            "not_applicable": optional_not_applicable,
        },
        "assumptions": sorted(value.get("assumptions", []) if isinstance(value.get("assumptions"), list) else [], key=lambda item: item.get("id", "") if isinstance(item, dict) else ""),
        "blockers": sorted(blockers, key=lambda item: (item.get("code", ""), item.get("path", ""), item.get("message", ""))),
        "human_approvals": sorted(approvals),
        "generated_files": generated_files,
        "validation_commands": [
            "python scripts/validate_agent_architecture.py --project . --json",
            "python scripts/audit_agent_safety.py --project . --json",
            "python -m unittest discover -s tests -v",
        ] + ([
            "pnpm --dir web test",
            "pnpm --dir web typecheck",
            "pnpm --dir web build",
        ] if overlays else []),
    }
    recipe["recipe_hash"] = content_hash(recipe)
    return recipe


def write_recipe(path: Path, recipe: dict[str, Any]) -> None:
    write_json(path, recipe)


def _configure_integrations(target: Path, blueprint: dict[str, Any]) -> None:
    selections = blueprint["implementation"]["optional_integrations"]
    profile = blueprint["implementation"]["profile"]
    config = read_json(target / "config/integrations.config.json")
    config["profile"] = profile
    config["channels"] = {"selection": selections["channels"], "default": None, "adapters": []}
    if selections["model_provider"] == "mock":
        providers = [{"id": "mock", "type": "mock", "enabled": True, "required": False, "credential_refs": {}, "settings": {"fixture": "deterministic"}}]
        default, fallback = "mock", ["mock"]
    else:
        providers, default, fallback = [], None, []
    config["model_providers"] = {"selection": selections["model_provider"], "default": default, "fallback_order": fallback, "providers": providers}
    config["mcp"] = {"selection": selections["mcp"], "servers": []}
    write_json(target / "config/integrations.config.json", config)


def _capability_matrix(blueprint: dict[str, Any], recipe: dict[str, Any]) -> dict[str, Any]:
    selected = set(recipe["capabilities"]["selected"])
    planned = set(recipe["capabilities"]["planned"])
    blocked = set(recipe["capabilities"]["blocked"])
    records = []
    required_capabilities = set(blueprint["capabilities"]["required"]) | set(recipe.get("derived_required", []))
    for capability in sorted(required_capabilities | set(blueprint["capabilities"]["optional"])):
        if capability in selected:
            status, evidence = "implemented", ["generated scaffold", f"factory/build-recipe.json#{capability}"]
        elif capability in blocked:
            status, evidence = "blocked", ["factory/build-recipe.json#blockers"]
        elif capability in planned:
            status, evidence = "planned", ["factory/assembly-manifest.json"]
        else:
            status, evidence = "not_applicable", ["factory/build-recipe.json#not_applicable"]
        records.append({
            "capability": capability,
            "required": capability in required_capabilities,
            "status": status,
            "phase": PHASE_BY_CAPABILITY.get(capability, "P0"),
            "files": ["factory/assembly-manifest.json"],
            "verification": "run applicable contract, safety, scenario, and eval gates",
            "evidence": evidence,
        })
    return {"version": "1.0", "blueprint_id": blueprint["blueprint_id"], "capabilities": records}


def _assembly_manifest(blueprint: dict[str, Any], recipe: dict[str, Any]) -> dict[str, Any]:
    capabilities = set(blueprint["capabilities"]["required"]) | set(blueprint["capabilities"]["optional"]) | set(recipe.get("derived_required", []))
    integrations = blueprint["implementation"]["optional_integrations"]
    return {
        "version": "1.0",
        "blueprint_id": blueprint["blueprint_id"],
        "perception": {"modalities": sorted(blueprint["perception"]["modalities"]), "sources": sorted(blueprint["perception"]["sources"]), "status": "planned"},
        "tools": {"status": "selected" if "tools" in capabilities else "not_applicable", "manifest": "config/tool-manifest.json"},
        "skills": {"status": "selected" if "skills" in capabilities else "not_applicable", "roots": ["skills"]},
        "knowledge": {"status": "planned" if "context" in capabilities else "not_applicable", "authorization_before_retrieval": True},
        "memory": {"status": "planned" if "memory" in capabilities else "not_applicable", "consent_required": blueprint["data_governance"]["consent_required"]},
        "model": {"selection": integrations["model_provider"], "status": "configuration_required" if integrations["model_provider"] in {"auto", "configured"} else "selected"},
        "channels": {"selection": integrations["channels"], "status": "planned" if integrations["channels"] == "configured" else "not_applicable"},
        "mcp": {"selection": integrations["mcp"], "status": "planned" if integrations["mcp"] == "configured" else "not_applicable"},
        "subagents": {"status": "planned" if "subagents" in capabilities else "not_applicable"},
        "instruction_provenance": {"source": "factory/agent-blueprint.json", "review_required": True, "immutable_safety_instructions": True},
        "recipe_hash": recipe["recipe_hash"],
    }


def _experience_manifest(blueprint: dict[str, Any], recipe: dict[str, Any]) -> dict[str, Any]:
    experience = normalize_profiles(blueprint)["experience"]
    profile = experience["profile"]
    default_surfaces = set()
    if profile == "browser_chat":
        default_surfaces = BROWSER_CHAT_SURFACES
    elif profile == "operations_console":
        default_surfaces = OPERATIONS_SURFACES
    surfaces = sorted(default_surfaces | _string_set(experience.get("surfaces")))
    generated = "browser-react-fastapi" in recipe.get("overlays", [])
    return {
        "version": "1.0",
        "blueprint_id": blueprint["blueprint_id"],
        "profile": profile,
        "reference_stack": experience["reference_stack"],
        "auth": experience["auth"],
        "realtime": experience["realtime"],
        "status": "not_applicable" if profile == "headless" else ("generated" if generated else "planned"),
        "generated_surfaces": surfaces if generated else [],
        "planned_surfaces": [] if generated else surfaces,
        "safe_events": list(SAFE_BROWSER_EVENTS) if profile != "headless" else [],
        "boundaries": {
            "api_executes_agent": False,
            "browser_resolves_credentials": False,
            "hidden_reasoning_exposed": False,
            "authorization_before_projection": True,
        },
        "recipe_hash": recipe["recipe_hash"],
    }


def _memory_manifest(blueprint: dict[str, Any], recipe: dict[str, Any]) -> dict[str, Any]:
    memory = normalize_profiles(blueprint)["memory"]
    enabled = bool(memory["enabled"])
    adapters = [memory["canonical_store"]]
    for key in ("keyword_index", "vector_index", "graph_store", "framework"):
        adapter = memory[key]
        if adapter not in {"none", "native"} and adapter not in adapters:
            adapters.append(adapter)
    governance = blueprint["data_governance"]
    return {
        "version": "1.0",
        "blueprint_id": blueprint["blueprint_id"],
        "enabled": enabled,
        "profile": memory["profile"],
        "status": "planned" if enabled else "not_applicable",
        "canonical_store": memory["canonical_store"],
        "keyword_index": memory["keyword_index"],
        "vector_index": memory["vector_index"],
        "graph_store": memory["graph_store"],
        "framework": memory["framework"],
        "adapters": adapters if enabled else [],
        "consent_required": governance["consent_required"],
        "retention_days": governance["retention_days"],
        "authorization_before_ranking": True,
        "one_canonical_store": True,
        "lifecycle": ["propose", "validate", "store", "retrieve", "correct", "expire", "delete", "reindex"],
        "recipe_hash": recipe["recipe_hash"],
    }


def _deployment_plan(blueprint: dict[str, Any], recipe: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_profiles(blueprint)
    experience = normalized["experience"]
    memory = normalized["memory"]
    engagement = normalized["delivery"]["engagement"]
    dependencies: set[str] = set()
    if experience["profile"] != "headless":
        dependencies.update({"python-fastapi-control-plane", "react-vite-build"})
    if memory["enabled"]:
        dependencies.add(memory["canonical_store"])
        for key in ("keyword_index", "vector_index", "graph_store", "framework"):
            value = memory[key]
            if value not in {"none", "native", memory["canonical_store"]}:
                dependencies.add(value)
    approval_gates = []
    if engagement in {"guided_install", "end_to_end"}:
        approval_gates.extend(["system_dependency_install", "secret_configuration", "network_exposure"])
        if memory["enabled"]:
            approval_gates.extend(["data_backup", "data_migration", "production_cutover"])
    return {
        "version": "1.0",
        "blueprint_id": blueprint["blueprint_id"],
        "engagement": engagement,
        "installation_allowed": False,
        "deployment_allowed": False,
        "dependencies": sorted(dependencies),
        "credential_policy": "secret_refs_only",
        "approval_gates": approval_gates,
        "validation_commands": list(recipe["validation_commands"]),
        "migration": {
            "required": bool(memory["enabled"] and memory["profile"] in {"hybrid", "enterprise"}),
            "strategy": "backup_sample_backfill_shadow_compare_approved_cutover",
        },
        "cutover": {"requires_human_approval": True, "automatic": False},
        "rollback": {"required": True, "verified_before_cutover": True},
        "recipe_hash": recipe["recipe_hash"],
    }


def apply_blueprint(blueprint: dict[str, Any], recipe: dict[str, Any], target: Path) -> dict[str, Any]:
    target = target.expanduser().resolve()
    generated = scaffold_project(
        recipe["scaffold"],
        blueprint["agent"]["name"],
        target,
        overlays=tuple(recipe.get("overlays", [])),
    )
    _configure_integrations(target, blueprint)
    factory = target / "factory"
    write_json(factory / "agent-blueprint.json", blueprint)
    write_json(factory / "build-recipe.json", recipe)
    write_json(factory / "capability-matrix.json", _capability_matrix(blueprint, recipe))
    write_json(factory / "assembly-manifest.json", _assembly_manifest(blueprint, recipe))
    experience_manifest = _experience_manifest(blueprint, recipe)
    write_json(factory / "experience-manifest.json", experience_manifest)
    write_json(target / "config" / "experience.config.json", experience_manifest)
    write_json(factory / "memory-manifest.json", _memory_manifest(blueprint, recipe))
    write_json(factory / "deployment-plan.json", _deployment_plan(blueprint, recipe))
    release = {
        "version": "1.0", "blueprint_id": blueprint["blueprint_id"],
        "status": "awaiting_human_approval",
        "automated_gates": [{"id": phase, "status": "pending", "evidence": []} for phase in recipe["applicable_phases"]],
        "required_approvals": recipe["human_approvals"],
        "prohibited_automation": ["production release", "high-risk permission grant", "credential acquisition"],
    }
    write_json(factory / "release-checklist.json", release)
    artifacts = sorted(recipe["generated_files"])
    return {
        "tool": "create_agent_from_blueprint", "status": "awaiting_human_approval",
        "target": str(target), "blueprint_id": blueprint["blueprint_id"],
        "generated_scaffold_files": len(generated), "artifacts": artifacts,
        "required_approvals": recipe["human_approvals"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan", type=Path)
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    if args.plan:
        plan_path = args.plan.expanduser().resolve()
        if plan_path == target or target in plan_path.parents:
            print("plan output must be outside the target project", file=sys.stderr)
            return 2
    try:
        blueprint = load_blueprint(args.blueprint.expanduser().resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"invalid blueprint: {exc}", file=sys.stderr)
        return 1
    recipe = build_recipe(blueprint)
    if args.plan:
        write_recipe(plan_path, recipe)
        return 1 if recipe["status"] == "blocked" else 0
    if recipe["status"] == "blocked":
        if args.report: write_json(args.report.expanduser().resolve(), {"tool": "create_agent_from_blueprint", "status": "blocked", "issues": recipe["blockers"]})
        return 1
    if target.exists() and any(target.iterdir()):
        print(f"target must be absent or empty: {target}", file=sys.stderr)
        return 2
    try:
        report = apply_blueprint(blueprint, recipe, target)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.report: write_json(args.report.expanduser().resolve(), report)
    else: print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
