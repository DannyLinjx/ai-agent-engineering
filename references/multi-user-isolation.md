# Multi-user and tenant isolation

Every resource and event must bind to `tenant_id` when applicable plus `user_id`, `channel_id`, `session_id`, `agent_id`, `workspace_id`, `run_id`, `skill_scope`, `memory_scope`, and `credential_scope`.

## Isolation boundaries

Enforce session, files/workspaces, skills, memory, credentials, MCP/model configuration, approvals, caches, queues, artifacts, logs, and eval datasets. Authorization filtering happens before retrieval or ranking, never after.

Use database row-level policy or mandatory scoped repositories, per-tenant object-store prefixes and keys, tenant-aware cache keys, isolated browser profiles, and short-lived scoped credentials. Do not rely on directory naming alone.

## Identity propagation

Authenticate at the interface and propagate an immutable principal through runtime, tools, jobs, checkpoints, hooks, subagents, MCP, and telemetry. Reject missing or conflicting scope. Background jobs revalidate authorization when resuming.

## Data lifecycle

Define retention, export, legal hold, deletion, backup isolation, and deletion propagation to derived artifacts, indexes, caches, and traces. Encrypt in transit and at rest; use tenant-specific keys where required.

## Tests

Use two tenants and two users with deliberately similar IDs. Attempt direct-ID access, search/retrieval leakage, cache collision, artifact URL guessing, queue/job takeover, skill/memory/credential crossover, log access, and deletion. Include concurrency tests, not just sequential unit tests.
