# Optional channels, model providers, and MCP

Treat channels, live model providers, and MCP servers as independently selectable adapters. Their absence must not block architecture work, scaffolding, unit tests, deterministic runtime tests, or offline evals.

## Configuration contract

Use one `integrations.config.json` validated by `schemas/integration-config.schema.json` and `scripts/validate_integration_config.py`. Generate a starting file with `scripts/configure_integrations.py`.

The three selections are independent:

- `channels.selection`: `none` or `configured`;
- `model_providers.selection`: `mock`, `none`, `auto`, or `configured`;
- `mcp.selection`: `none` or `configured`.

Default development/test configuration is no channel, a deterministic mock model, and no MCP server. This is a valid core configuration. Do not ask the user to choose an external integration unless their requested outcome actually depends on it.

## Supported channel adapters

The reference catalog supports `cli`, `web`, `api`, `webhook`, `telegram`, `feishu`, `lark`, `wecom`, `wechat_official_account`, `slack`, `discord`, `microsoft_teams`, and `email`. Treat Feishu and international Lark as separate configuration types even when they share an implementation family. `wecom` means 企业微信.

Every channel adapter declares stable ID, type, enabled/required flags, credential references, and provider-specific settings. Implement a common contract for inbound normalization, outbound send, health, and shutdown. Normalize tenant/user/channel/conversation/message IDs, locale, attachments, idempotency key, reply target, and cancellation.

No channel is a valid selection. A runtime may be exercised through direct API calls, a CLI harness, or test fixtures without registering a messaging channel.

## Model provider selection

Supported provider types include `mock`, `openai`, `azure_openai`, `anthropic`, `google`, `openrouter`, `ollama`, `vllm`, `bedrock`, `vertex_ai`, and `custom_openai_compatible`.

- `mock`: deterministic development/test provider; never claim live-model or production readiness from it.
- `none`: provider adapter work is intentionally deferred; model-dependent live tests are skipped.
- `auto`: choose among configured compatible providers by capabilities, privacy, availability, budget, and latency.
- `configured`: use the declared default provider and fallback order.

Core runtime tests use a scripted/mock gateway and must not depend on an API key. A live provider is required only when the requested acceptance criterion requires live inference or the profile is `production`. If the user has not selected one, complete all independent work and report the live-provider gate as `skipped` for development/test or `blocked` for production—not as a generic project test failure.

## MCP selection

MCP is optional. `none` means no connection, discovery, or MCP acceptance tests. `configured` declares zero or more task-scoped server adapters using `stdio`, `streamable_http`, or `sse`; at least one enabled server is then required.

MCP server absence must not fail core tool/runtime tests. When configured, validate transport settings and credential references, then run health/discovery/tool-adapter tests only for enabled servers. A server marked `required: true` may block only the capability or profile that explicitly requires it.

## Credentials

Configuration contains references such as `secret://agent/openai/api_key`, `env://OPENAI_API_KEY`, or `vault://team/path#field`; it never contains raw tokens, passwords, app secrets, cookies, or private keys. Resolve references at runtime through a credential provider and inject only into the selected adapter.

## Test policy

Partition acceptance evidence:

| Suite | No integration configured | Configured integration |
|---|---|---|
| core contracts/runtime/permissions/context/checkpoint | run and must pass | run and must pass |
| mock model scenarios/offline eval | run and must pass | run and must pass |
| live model provider | `skipped` in dev/test; blocked only for production | run for enabled provider |
| channel adapter | `not_applicable`/`skipped` | run for enabled adapters |
| MCP adapter | `not_applicable`/`skipped` | run for enabled servers |

Never turn an unselected optional adapter into a required failure. Never turn a skipped live integration into evidence that it works. Production readiness requires a real model provider; channels and MCP remain optional unless the product charter marks them required.

## Examples

Default core-only configuration:

```bash
python scripts/configure_integrations.py --output config/integrations.config.json
python scripts/validate_integration_config.py --config config/integrations.config.json --profile development
```

Feishu plus 企业微信, an OpenAI provider, and a GitHub MCP stub:

```bash
python scripts/configure_integrations.py \
  --channel feishu --channel wecom \
  --model-provider openai \
  --mcp-server github=stdio \
  --output config/integrations.config.json
```

The generator writes credential references and editable settings only. It does not request, store, or test real secrets.
