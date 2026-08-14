#!/usr/bin/env python3
"""Validate a generated Browser Experience Manifest without starting the application."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import emit, issue, read_json, result

PROFILES = {"headless", "browser_chat", "operations_console"}
STACKS = {"none", "react_fastapi"}
AUTH = {"none", "local_account", "server_session", "oidc"}
REALTIME = {"none", "sse", "websocket"}
STATUSES = {"not_applicable", "planned", "generated"}
SAFE_EVENTS = {
    "approval.required", "approval.resolved", "artifact.created", "evidence.added",
    "memory.proposed", "memory.rejected", "memory.stored", "plan.updated",
    "run.status", "step.completed", "step.failed", "step.started", "tool.completed",
    "tool.failed", "tool.started", "verification.completed",
}
REQUIRED = {
    "version", "blueprint_id", "profile", "reference_stack", "auth", "realtime", "status",
    "generated_surfaces", "planned_surfaces", "safe_events", "boundaries", "recipe_hash",
}


def validate_manifest(value: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [issue("invalid-manifest", "Experience Manifest must be an object")]
    for key in sorted(REQUIRED - set(value)):
        findings.append(issue("missing-field", "Required field is missing", path=key))
    for key in sorted(set(value) - REQUIRED):
        findings.append(issue("unknown-field", "Unknown Experience Manifest field", path=key))
    for path, allowed in (
        ("profile", PROFILES), ("reference_stack", STACKS), ("auth", AUTH),
        ("realtime", REALTIME), ("status", STATUSES),
    ):
        if value.get(path) not in allowed:
            findings.append(issue("invalid-enum", f"Expected one of {sorted(allowed)}", path=path))
    for field in ("generated_surfaces", "planned_surfaces", "safe_events"):
        items = value.get(field)
        if not isinstance(items, list) or not all(isinstance(item, str) and item for item in items):
            findings.append(issue("invalid-list", "Expected a list of non-empty strings", path=field))
        elif len(items) != len(set(items)):
            findings.append(issue("duplicate-item", "List entries must be unique", path=field))
    safe_events = value.get("safe_events")
    if isinstance(safe_events, list):
        for index, event in enumerate(safe_events):
            if event not in SAFE_EVENTS:
                findings.append(issue("unsafe-event", "Event is not in the browser projection allowlist", path=f"safe_events[{index}]"))
    boundaries = value.get("boundaries")
    expected_boundaries = {
        "api_executes_agent": False,
        "browser_resolves_credentials": False,
        "hidden_reasoning_exposed": False,
        "authorization_before_projection": True,
    }
    if boundaries != expected_boundaries:
        findings.append(issue("unsafe-boundary", "Experience boundaries must preserve API, credential, reasoning, and authorization controls", path="boundaries"))
    profile = value.get("profile")
    if profile == "headless":
        if value.get("reference_stack") != "none" or value.get("auth") != "none" or value.get("realtime") != "none":
            findings.append(issue("headless-profile-conflict", "Headless manifest cannot enable browser components", path="profile"))
    elif profile in {"browser_chat", "operations_console"}:
        if value.get("reference_stack") == "none" or value.get("auth") == "none" or value.get("realtime") == "none":
            findings.append(issue("incomplete-browser-profile", "Browser manifest requires stack, auth, and realtime transport", path="profile"))
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
    output = result("validate_experience_manifest", path, findings)
    emit(output, json_output=args.json)
    return 1 if output["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
