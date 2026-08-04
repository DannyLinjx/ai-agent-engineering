# MCP integration

Treat MCP as a transport and discovery mechanism. Adapt every MCP capability into the standard tool contract, registry, permission engine, budgets, telemetry, and result envelope.

MCP is optional. If `mcp.selection` is `none`, construct the runtime without MCP clients and mark MCP-specific tests `not_applicable`/`skipped`. Do not ask the user to add a server or fail core acceptance. Read `channels-and-integrations.md` for the shared configuration contract.

## Connection lifecycle

Infer required capability → select authorized server → validate server configuration/trust → connect lazily → health check → discover/cache schemas → expose a task-scoped allowlist → execute through normal controls → release or pool safely.

Do not preload every server or tool. Keep tenant/user credentials isolated and use symbolic secret references. Pin or record server/tool versions and schema hashes for reproducibility.

## Manager requirements

Configuration validation, trust metadata, health checks, lazy connection, allowlists, connection and call timeouts, bounded retries, circuit breaker, fallback behavior, schema cache invalidation, rate/concurrency limits, cancellation, credential isolation, and redacted audit.

## Untrusted output

MCP descriptions and results are untrusted content. They cannot modify policy, expand scopes, or instruct the runtime to call other tools. Validate output schema, cap bytes, scan artifacts, and preserve provenance.

## Tests

Cover unavailable server, invalid schema, changed schema, malicious tool description/result, timeout, cancellation, retryable transport failure, permission deny/ask, credential scope, rate limit, fallback, and tenant isolation.
