#!/usr/bin/env python3
"""Generate an optional Channel, Model Provider, and MCP configuration without collecting secrets."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from _common import write_json

CHANNELS = ("cli", "web", "api", "webhook", "telegram", "feishu", "lark", "wecom", "wechat_official_account", "slack", "discord", "microsoft_teams", "email")
PROVIDERS = ("openai", "azure_openai", "anthropic", "google", "openrouter", "ollama", "vllm", "bedrock", "vertex_ai", "custom_openai_compatible")
TRANSPORTS = ("stdio", "streamable_http", "sse")

CHANNEL_CREDENTIALS = {
    "telegram": ("bot_token",), "feishu": ("app_id", "app_secret", "verification_token"),
    "lark": ("app_id", "app_secret", "verification_token"),
    "wecom": ("corp_id", "app_secret", "callback_token", "encoding_aes_key"),
    "wechat_official_account": ("app_id", "app_secret", "callback_token", "encoding_aes_key"),
    "slack": ("bot_token", "signing_secret"), "discord": ("bot_token",),
    "microsoft_teams": ("tenant_id", "client_id", "client_secret"),
    "email": ("username", "password"), "webhook": ("signing_secret",)
}
PROVIDER_CREDENTIALS = {
    "openai": ("api_key",), "azure_openai": ("api_key",), "anthropic": ("api_key",),
    "google": ("api_key",), "openrouter": ("api_key",), "bedrock": ("access_key_id", "secret_access_key"),
    "vertex_ai": ("service_account",), "custom_openai_compatible": ("api_key",)
}

def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    if not result: raise argparse.ArgumentTypeError(f"invalid identifier: {value}")
    return result

def refs(kind: str, name: str, keys: tuple[str, ...]) -> dict[str, str]:
    return {key: f"secret://agent/{kind}/{name}/{key}" for key in keys}

def parse_mcp(value: str) -> tuple[str, str]:
    name, separator, transport = value.partition("=")
    transport = transport if separator else "stdio"
    if transport not in TRANSPORTS: raise argparse.ArgumentTypeError(f"unsupported MCP transport: {transport}")
    return slug(name), transport

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", choices=("development", "test", "production"), default="development")
    parser.add_argument("--channel", action="append", choices=CHANNELS, default=[])
    parser.add_argument("--default-channel")
    parser.add_argument("--model-provider", action="append", choices=PROVIDERS, default=[])
    parser.add_argument("--model-selection", choices=("mock", "none", "auto", "configured"))
    parser.add_argument("--default-model")
    parser.add_argument("--mcp-server", action="append", type=parse_mcp, default=[], metavar="ID[=TRANSPORT]")
    args = parser.parse_args()

    channel_items = []
    for index, channel_type in enumerate(dict.fromkeys(args.channel)):
        channel_id = f"{channel_type}-{index + 1}"
        settings: dict[str, object] = {}
        if channel_type in {"feishu", "lark", "wecom", "wechat_official_account", "telegram", "slack", "discord", "microsoft_teams"}: settings["event_mode"] = "webhook"
        channel_items.append({"id": channel_id, "type": channel_type, "enabled": True, "required": False, "credential_refs": refs("channels", channel_id, CHANNEL_CREDENTIALS.get(channel_type, ())), "settings": settings})
    channel_default = args.default_channel or (channel_items[0]["id"] if channel_items else None)
    if channel_default is not None and channel_default not in {item["id"] for item in channel_items}: parser.error("--default-channel must match a generated channel ID")

    model_selection = args.model_selection or ("configured" if args.model_provider else "mock")
    if model_selection in {"auto", "configured"} and not args.model_provider: parser.error(f"{model_selection} requires --model-provider")
    if model_selection in {"mock", "none"} and args.model_provider: parser.error(f"{model_selection} cannot be combined with --model-provider")
    if args.profile == "production" and model_selection in {"mock", "none"}: parser.error("production requires --model-provider and model selection auto/configured")
    provider_items = []
    if model_selection == "mock":
        provider_items = [{"id": "mock", "type": "mock", "enabled": True, "required": False, "credential_refs": {}, "settings": {"fixture": "deterministic"}}]
    else:
        for index, provider_type in enumerate(dict.fromkeys(args.model_provider)):
            provider_id = f"{provider_type}-{index + 1}"
            settings: dict[str, object] = {"model": "SET_ME"}
            if provider_type in {"ollama", "vllm", "custom_openai_compatible"}: settings["base_url"] = "SET_ME"
            provider_items.append({"id": provider_id, "type": provider_type, "enabled": True, "required": False, "credential_refs": refs("models", provider_id, PROVIDER_CREDENTIALS.get(provider_type, ())), "settings": settings})
    provider_ids = [item["id"] for item in provider_items]
    model_default = args.default_model or (provider_ids[0] if provider_ids else None)
    if model_default is not None and model_default not in provider_ids: parser.error("--default-model must match a generated provider ID")

    mcp_items = []
    for server_id, transport in dict.fromkeys(args.mcp_server):
        settings = {"command": "SET_ME", "args": []} if transport == "stdio" else {"url": "SET_ME"}
        mcp_items.append({"id": server_id, "transport": transport, "enabled": True, "required": False, "credential_refs": {}, "settings": settings})

    config = {
        "version": "1.0", "profile": args.profile,
        "channels": {"selection": "configured" if channel_items else "none", "default": channel_default, "adapters": channel_items},
        "model_providers": {"selection": model_selection, "default": model_default, "fallback_order": provider_ids, "providers": provider_items},
        "mcp": {"selection": "configured" if mcp_items else "none", "servers": mcp_items},
        "test_policy": {"unconfigured_optional": "skip", "require_live_model_for_profiles": ["production"], "fail_on_skipped_required": True}
    }
    write_json(args.output.expanduser().resolve(), config)
    print(f"wrote optional integration config: {args.output.expanduser().resolve()}")
    print(f"channels={config['channels']['selection']} model={model_selection} mcp={config['mcp']['selection']}")
    print("credential values were not collected; edit settings and resolve secret:// references at runtime")
    return 0

if __name__ == "__main__": raise SystemExit(main())
