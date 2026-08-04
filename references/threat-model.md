# Agent threat model

Create this during P0 and update it whenever tools, data, identity, models, MCP servers, channels, or deployment boundaries change.

## Assets

User/tenant data, credentials, source code, workspaces, prompts and system rules, memory, artifacts, approvals, audit trails, model/tool budgets, external accounts, production systems, and reputation.

## Trust boundaries

Interface to runtime, runtime to model provider, model decision to deterministic executor, workspace to host, tenant to tenant, runtime to storage/queue, tool to external service, MCP server to registry, subagent to parent, and artifact renderer to user.

## Threat categories

- direct and indirect prompt injection;
- tool/skill/MCP description poisoning;
- argument injection, shell injection, path traversal, symlink escape;
- SSRF, DNS rebinding, malicious downloads, data exfiltration;
- credential exposure in context, memory, logs, artifacts, or approvals;
- excessive agency, approval confusion, time-of-check/time-of-use mutation;
- destructive or irreversible side effects and duplicate execution;
- tenant crossover through repositories, caches, queues, search, browser profiles, or observability;
- checkpoint/state tampering, replay, race, and stale configuration;
- dependency/provider compromise, schema drift, and supply-chain attack;
- denial of service through loops, fan-out, output volume, or cost;
- evaluator manipulation and false completion evidence.

## Controls

For each threat record preventive, detective, and recovery controls; owner; verification; residual risk; and accepted/mitigated status. High-value controls include typed schemas, least privilege, deterministic policy, scoped credentials, isolated sandboxes, output caps, egress allowlists, content provenance, artifact scanning, idempotency, append-only audit, budgets, and kill switches.

## Abuse cases to test

Untrusted file/web content asks the agent to reveal secrets or change rules; a tool result names an unregistered tool; a path traverses or escapes via symlink; a command hides destructive behavior; an upload includes restricted data; an approval is replayed with changed parameters; two tenants use the same cache/search key; a crashed non-idempotent call is retried; a subagent exceeds scope; an evaluator is fooled by a fabricated success message.
