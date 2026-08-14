#!/usr/bin/env python3
"""Validate a generated Memory Manifest without contacting its declared backends."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import emit, issue, read_json, result

PROFILES = {"local", "hybrid", "enterprise"}
CANONICAL_STORES = {"sqlite", "postgresql"}
KEYWORD_INDEXES = {"none", "sqlite_fts5", "postgres_fts"}
VECTOR_INDEXES = {"none", "pgvector", "redis", "qdrant", "milvus", "weaviate", "mem0"}
GRAPH_STORES = {"none", "neo4j", "mem0"}
FRAMEWORKS = {"native", "mem0"}
STATUSES = {"not_applicable", "planned", "generated"}
REQUIRED = {
    "version", "blueprint_id", "enabled", "profile", "status", "canonical_store",
    "keyword_index", "vector_index", "graph_store", "framework", "adapters",
    "consent_required", "retention_days", "authorization_before_ranking",
    "one_canonical_store", "lifecycle", "recipe_hash",
}


def validate_manifest(value: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [issue("invalid-manifest", "Memory Manifest must be an object")]
    for key in sorted(REQUIRED - set(value)):
        findings.append(issue("missing-field", "Required field is missing", path=key))
    for key in sorted(set(value) - REQUIRED):
        findings.append(issue("unknown-field", "Unknown Memory Manifest field", path=key))
    for path, allowed in (
        ("profile", PROFILES), ("status", STATUSES), ("canonical_store", CANONICAL_STORES),
        ("keyword_index", KEYWORD_INDEXES), ("vector_index", VECTOR_INDEXES),
        ("graph_store", GRAPH_STORES), ("framework", FRAMEWORKS),
    ):
        if value.get(path) not in allowed:
            findings.append(issue("invalid-enum", f"Expected one of {sorted(allowed)}", path=path))
    for field in ("enabled", "consent_required", "authorization_before_ranking", "one_canonical_store"):
        if not isinstance(value.get(field), bool):
            findings.append(issue("invalid-type", "Expected a boolean", path=field))
    if value.get("authorization_before_ranking") is not True:
        findings.append(issue("unsafe-retrieval-order", "Authorization must happen before Memory ranking", path="authorization_before_ranking"))
    if value.get("one_canonical_store") is not True:
        findings.append(issue("multiple-canonical-stores", "Exactly one canonical Memory store is required", path="one_canonical_store"))
    retention = value.get("retention_days")
    if not isinstance(retention, int) or isinstance(retention, bool) or retention < 0:
        findings.append(issue("invalid-retention", "Retention days must be a non-negative integer", path="retention_days"))
    for field in ("adapters", "lifecycle"):
        items = value.get(field)
        if not isinstance(items, list) or not all(isinstance(item, str) and item for item in items):
            findings.append(issue("invalid-list", "Expected a list of non-empty strings", path=field))
        elif len(items) != len(set(items)):
            findings.append(issue("duplicate-item", "List entries must be unique", path=field))
    if value.get("enabled"):
        profile = value.get("profile")
        canonical = value.get("canonical_store")
        if profile in {"hybrid", "enterprise"} and canonical != "postgresql":
            findings.append(issue("enterprise-canonical-store", "Hybrid and enterprise Memory require PostgreSQL", path="canonical_store"))
        if profile == "local" and canonical != "sqlite":
            findings.append(issue("local-canonical-store", "Local Memory requires SQLite", path="canonical_store"))
        adapters = value.get("adapters")
        if isinstance(adapters, list) and canonical not in adapters:
            findings.append(issue("canonical-adapter-missing", "Canonical store must appear in adapters", path="adapters"))
    elif value.get("status") != "not_applicable":
        findings.append(issue("disabled-status", "Disabled Memory must be not_applicable", path="status"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = args.manifest.expanduser().resolve()
    try:
        value = read_json(path)
        findings = validate_manifest(value)
    except (OSError, ValueError) as exc:
        findings = [issue("invalid-json", str(exc))]
    output = result("validate_memory_manifest", path, findings)
    emit(output, json_output=args.json)
    return 1 if output["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
