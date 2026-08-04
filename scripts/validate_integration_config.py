#!/usr/bin/env python3
"""Validate optional integrations and classify which acceptance suites should run or skip."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from _common import emit, issue, read_json, result

CHANNEL_TYPES = {"cli", "web", "api", "webhook", "telegram", "feishu", "lark", "wecom", "wechat_official_account", "slack", "discord", "microsoft_teams", "email"}
PROVIDER_TYPES = {"mock", "openai", "azure_openai", "anthropic", "google", "openrouter", "ollama", "vllm", "bedrock", "vertex_ai", "custom_openai_compatible"}
TRANSPORTS = {"stdio", "streamable_http", "sse"}
REF = re.compile(r"^(secret|env|vault)://.+")
SECRET_KEY = re.compile(r"(?i)(api.?key|password|secret|token|cookie|private.?key|authorization|aes.?key)")

def section(config: Any, key: str, issues: list[dict]) -> dict[str, Any]:
    value = config.get(key) if isinstance(config, dict) else None
    if not isinstance(value, dict): issues.append(issue("missing-section", f"{key} must be an object", path=key)); return {}
    return value

def validate_items(items: Any, *, kind: str, allowed: set[str], type_key: str, issues: list[dict]) -> tuple[list[dict], set[str]]:
    if not isinstance(items, list): issues.append(issue("invalid-items", f"{kind} items must be an array", path=kind)); return [], set()
    valid, ids = [], set()
    for index, item in enumerate(items):
        path = f"{kind}[{index}]"
        if not isinstance(item, dict): issues.append(issue("invalid-item", "Item must be an object", path=path)); continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id: issues.append(issue("invalid-id", "Item requires a non-empty id", path=path)); continue
        if item_id in ids: issues.append(issue("duplicate-id", f"Duplicate id: {item_id}", path=path))
        ids.add(item_id)
        if item.get(type_key) not in allowed: issues.append(issue("unsupported-type", f"Unsupported {type_key}: {item.get(type_key)}", path=path))
        if not isinstance(item.get("enabled"), bool) or not isinstance(item.get("required"), bool): issues.append(issue("invalid-flags", "enabled and required must be booleans", path=path))
        if item.get("required") and not item.get("enabled"): issues.append(issue("required-disabled", "A required integration cannot be disabled", path=path))
        refs = item.get("credential_refs")
        if not isinstance(refs, dict): issues.append(issue("invalid-credential-refs", "credential_refs must be an object", path=path))
        else:
            for name, ref in refs.items():
                if not isinstance(ref, str) or not REF.match(ref): issues.append(issue("raw-or-invalid-credential", f"Credential {name} must use secret://, env://, or vault://", path=path))
        settings = item.get("settings")
        if not isinstance(settings, dict): issues.append(issue("invalid-settings", "settings must be an object", path=path))
        else:
            for name, value in settings.items():
                if SECRET_KEY.search(str(name)) and isinstance(value, str) and not REF.match(value): issues.append(issue("inline-secret", f"Secret-like setting {name} must be moved to credential_refs", path=path))
        valid.append(item)
    return valid, ids

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--profile", choices=("development", "test", "production"), help="Override config profile for gate evaluation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = args.config.expanduser().resolve()
    try: config = read_json(path)
    except (OSError, ValueError) as exc:
        value = result("validate_integration_config", path, [issue("invalid-json", str(exc))]); emit(value, json_output=args.json); return 1
    issues: list[dict] = []
    if not isinstance(config, dict): issues.append(issue("invalid-config", "Top-level config must be an object")); config = {}
    profile = args.profile or config.get("profile")
    if profile not in {"development", "test", "production"}: issues.append(issue("invalid-profile", "profile must be development, test, or production", path="profile")); profile = "development"

    channels = section(config, "channels", issues)
    channel_items, channel_ids = validate_items(channels.get("adapters", []), kind="channels.adapters", allowed=CHANNEL_TYPES, type_key="type", issues=issues)
    channel_selection = channels.get("selection")
    enabled_channels = [item for item in channel_items if item.get("enabled")]
    if channel_selection == "none" and channel_items: issues.append(issue("none-has-items", "channels.selection=none requires an empty adapters array", path="channels"))
    elif channel_selection == "configured" and not enabled_channels: issues.append(issue("configured-empty", "Configured channels require at least one enabled adapter", path="channels"))
    elif channel_selection not in {"none", "configured"}: issues.append(issue("invalid-selection", "Channel selection must be none or configured", path="channels.selection"))
    if channels.get("default") is not None and channels.get("default") not in channel_ids: issues.append(issue("invalid-default", "Default channel must reference an adapter id", path="channels.default"))

    providers = section(config, "model_providers", issues)
    provider_items, provider_ids = validate_items(providers.get("providers", []), kind="model_providers.providers", allowed=PROVIDER_TYPES, type_key="type", issues=issues)
    provider_selection = providers.get("selection")
    enabled_providers = [item for item in provider_items if item.get("enabled")]
    live_providers = [item for item in enabled_providers if item.get("type") != "mock"]
    if provider_selection == "none" and (provider_items or providers.get("default") is not None or providers.get("fallback_order")): issues.append(issue("none-has-items", "model_providers.selection=none requires no providers/default/fallback", path="model_providers"))
    elif provider_selection == "mock" and (not enabled_providers or any(item.get("type") != "mock" for item in enabled_providers)): issues.append(issue("invalid-mock-selection", "Mock selection requires an enabled mock provider only", path="model_providers"))
    elif provider_selection in {"auto", "configured"} and not live_providers: issues.append(issue("configured-empty", "Auto/configured model selection requires an enabled live provider", path="model_providers"))
    elif provider_selection not in {"none", "mock", "auto", "configured"}: issues.append(issue("invalid-selection", "Invalid model provider selection", path="model_providers.selection"))
    if providers.get("default") is not None and providers.get("default") not in provider_ids: issues.append(issue("invalid-default", "Default model must reference a provider id", path="model_providers.default"))
    fallback = providers.get("fallback_order")
    if not isinstance(fallback, list) or any(item not in provider_ids for item in fallback): issues.append(issue("invalid-fallback", "fallback_order must contain provider ids", path="model_providers.fallback_order"))
    if profile == "production" and not live_providers: issues.append(issue("live-model-required", "Production requires at least one enabled non-mock model provider", path="model_providers"))

    mcp = section(config, "mcp", issues)
    mcp_items, _ = validate_items(mcp.get("servers", []), kind="mcp.servers", allowed=TRANSPORTS, type_key="transport", issues=issues)
    mcp_selection = mcp.get("selection")
    enabled_mcp = [item for item in mcp_items if item.get("enabled")]
    if mcp_selection == "none" and mcp_items: issues.append(issue("none-has-items", "mcp.selection=none requires an empty servers array", path="mcp"))
    elif mcp_selection == "configured" and not enabled_mcp: issues.append(issue("configured-empty", "Configured MCP requires at least one enabled server", path="mcp"))
    elif mcp_selection not in {"none", "configured"}: issues.append(issue("invalid-selection", "MCP selection must be none or configured", path="mcp.selection"))

    test_policy = section(config, "test_policy", issues)
    if test_policy.get("unconfigured_optional") != "skip": issues.append(issue("unsafe-test-policy", "Unconfigured optional integrations must be skipped", path="test_policy.unconfigured_optional"))
    if test_policy.get("fail_on_skipped_required") is not True: issues.append(issue("unsafe-test-policy", "Skipped required integrations must fail", path="test_policy.fail_on_skipped_required"))

    matrix = {
        "core": "run", "mock_model": "run" if provider_selection == "mock" else "skipped",
        "live_model": "run" if live_providers else ("blocked" if profile == "production" else "skipped"),
        "channels": "run" if enabled_channels else "skipped", "mcp": "run" if enabled_mcp else "skipped"
    }
    value = result("validate_integration_config", path, issues, {"profile": profile, "selections": {"channels": channel_selection, "model_providers": provider_selection, "mcp": mcp_selection}, "enabled": {"channels": len(enabled_channels), "live_model_providers": len(live_providers), "mcp_servers": len(enabled_mcp)}, "test_matrix": matrix})
    emit(value, json_output=args.json)
    return 1 if value["status"] == "failed" else 0

if __name__ == "__main__": raise SystemExit(main())
