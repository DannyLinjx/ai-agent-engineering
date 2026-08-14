#!/usr/bin/env python3
"""Generate a deterministic, non-mutating Memory topology and migration plan."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from _common import write_json


REQUIRED = {
    "profile",
    "users",
    "tenant_count",
    "expected_records",
    "concurrent_writers",
    "latency_target_ms",
    "availability_target",
    "semantic_retrieval_required",
    "graph_queries",
    "graph_acceptance_cases",
    "managed_preference",
    "data_class",
    "engagement",
}


def _hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate(request: dict[str, Any]) -> None:
    if set(request) != REQUIRED:
        raise ValueError(f"request must contain exactly {sorted(REQUIRED)}")
    enums = {
        "profile": {"local", "hybrid", "enterprise"},
        "managed_preference": {"managed", "self_hosted", "either"},
        "data_class": {"public", "internal", "confidential", "restricted"},
        "engagement": {"plan_only", "guided_install", "end_to_end"},
    }
    for name, allowed in enums.items():
        if request[name] not in allowed:
            raise ValueError(f"{name} must be one of {sorted(allowed)}")
    for name in ("users", "tenant_count", "expected_records", "concurrent_writers", "latency_target_ms"):
        if not isinstance(request[name], int) or isinstance(request[name], bool) or request[name] < 1:
            raise ValueError(f"{name} must be a positive integer")
    availability = request["availability_target"]
    if not isinstance(availability, (int, float)) or isinstance(availability, bool) or not 0 < availability <= 1:
        raise ValueError("availability_target must be in (0, 1]")
    if not isinstance(request["semantic_retrieval_required"], bool):
        raise ValueError("semantic_retrieval_required must be boolean")
    for name in ("graph_queries", "graph_acceptance_cases"):
        if not isinstance(request[name], list) or not all(isinstance(item, str) and item.strip() for item in request[name]):
            raise ValueError(f"{name} must be a list of non-empty strings")
    if request["graph_queries"] and not request["graph_acceptance_cases"]:
        raise ValueError("graph acceptance case is required before selecting a graph store")


def build_deployment_plan(request: dict[str, Any]) -> dict[str, Any]:
    _validate(request)
    profile = request["profile"]
    local = profile == "local"
    canonical = "sqlite" if local else "postgresql"
    keyword = "sqlite_fts5" if local else "postgres_fts"
    vector = "pgvector" if not local and request["semantic_retrieval_required"] else "none"
    graph = "neo4j" if request["graph_queries"] else "none"
    cache = "redis" if not local and (request["concurrent_writers"] >= 50 or request["latency_target_ms"] <= 100) else "none"
    services: list[dict[str, Any]] = []
    if not local:
        services.append({"name": "postgresql", "ports": [5432], "volume": "memory-postgresql-data", "credential_ref": "secret://memory/postgresql"})
    if cache == "redis":
        services.append({"name": "redis", "ports": [6379], "volume": "memory-redis-data", "credential_ref": "secret://memory/redis"})
    if graph == "neo4j":
        services.append({"name": "neo4j", "ports": [7474, 7687], "volume": "memory-neo4j-data", "credential_ref": "secret://memory/neo4j"})
    dependencies = [canonical, keyword]
    dependencies.extend(item for item in (vector, graph, cache) if item != "none")
    approvals: list[str] = []
    if request["engagement"] in {"guided_install", "end_to_end"}:
        approvals.extend(["system_dependency_install", "secret_configuration", "network_exposure"])
        if not local:
            approvals.extend(["data_backup", "data_migration", "production_cutover"])
    migration = {
        "required": not local,
        "steps": [] if local else [
            "verify source backup and restore",
            "validate sample export and import",
            "bulk backfill canonical records",
            "enable lifecycle outbox dual projection",
            "compare shadow reads against acceptance thresholds",
            "obtain human cutover approval",
            "monitor rollback window",
        ],
        "cutover_requires_human_approval": True,
        "automatic_cutover": False,
    }
    plan = {
        "version": "1.0",
        "status": "planned",
        "request_hash": _hash(request),
        "profile": profile,
        "engagement": request["engagement"],
        "installation_allowed": False,
        "deployment_allowed": False,
        "selection_reasons": [
            "SQLite/FTS5 is the smallest local canonical topology" if local else "PostgreSQL is the shared canonical store for hybrid and enterprise profiles",
            "semantic retrieval was explicitly required" if vector != "none" else "no measured vector requirement was declared",
            "graph queries have acceptance coverage" if graph != "none" else "no graph query acceptance requirement was declared",
            "Redis is selected only for declared concurrency or latency pressure" if cache != "none" else "no independent cache service is required",
        ],
        "topology": {
            "canonical_store": canonical,
            "keyword_index": keyword,
            "vector_index": vector,
            "graph_store": graph,
            "cache": cache,
            "framework": "native",
            "one_canonical_store": True,
        },
        "dependencies": sorted(set(dependencies)),
        "services": services,
        "credential_policy": "secret_refs_only",
        "approval_gates": approvals,
        "backup": {
            "required": True,
            "restore_test_required": True,
            "strategy": "SQLite snapshot and integrity check" if local else "PostgreSQL base backup plus point-in-time recovery",
        },
        "migration": migration,
        "validation": [
            "scope isolation and authorization-before-ranking",
            "consent, secret rejection, correction, expiry, and deletion",
            "backup restore and index rebuild",
            "outbox reconciliation and lag threshold",
            "shadow-read comparison before cutover" if not local else "restart persistence and deterministic export",
        ],
        "rollback": {
            "required": True,
            "verified_before_cutover": True,
            "strategy": "retain source read path until reconciliation and rollback window complete",
        },
        "operational_ownership_required": bool(services),
    }
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    request_path = args.request.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if request_path == output_path:
        print("request and output paths must differ", file=sys.stderr)
        return 2
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
        if not isinstance(request, dict):
            raise ValueError("request root must be an object")
        plan = build_deployment_plan(request)
        write_json(output_path, plan)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"wrote non-mutating Memory deployment plan to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
