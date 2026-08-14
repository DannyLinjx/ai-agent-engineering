# Reference architecture

Design the runtime as replaceable modules connected by explicit contracts. The model proposes; deterministic code validates, authorizes, executes, persists, and verifies.

## Layer model

1. **Interface** — optional CLI, web, API, IDE, Telegram, Feishu/Lark, WeCom/企业微信, Slack, Discord, Teams, email, webhook, or automation adapters. Normalize identity, channel, locale, attachments, cancel signal, and response streaming. A core runtime may have no registered channel.
2. **Identity, tenant, session, workspace** — authenticate, resolve scopes, enforce workspace roots, and open or resume a session.
3. **Orchestrator** — classify intent, select mode, create a plan, schedule steps, maintain state, and apply termination rules.
4. **Context, memory, skill selection** — build only the task-relevant context under a measured token budget.
5. **Model query engine** — select provider/model, stream, validate structured output, retry transient failures, honor cancellation/deadlines, and meter cost.
6. **Permission and hooks** — evaluate deterministic policy and lifecycle controls before any side effect.
7. **Tool registry and executor** — expose atomic capabilities through schemas and bounded execution.
8. **External resources** — files, processes, browser, source control, databases, MCP servers, enterprise apps.
9. **Sidecar services** — persistence, checkpoints, artifacts, audit, traces, metrics, evaluation, subagents, and model routing.

See `assets/architecture-diagram.mmd` for the data flow.

For a Browser Experience, the interface becomes a separate control plane as shown in
`../assets/browser-control-plane.mmd`: request handlers authenticate, authorize, and
persist commands; a Worker invokes the Agent Runtime; the browser consumes safe,
durable projections. Never place Agent execution or credential resolution in the API
request path.

For durable Memory, follow `../assets/memory-platform.mmd`: one canonical store owns
records, while FTS, vector, graph, and framework integrations consume lifecycle
events as rebuildable projections. Authorization filters candidates before ranking.

## Required dependency direction

Domain contracts must not depend on provider SDKs, CLI frameworks, databases, or MCP libraries. Adapters depend inward on contracts. The orchestrator consumes interfaces such as `ModelGateway`, `ToolExecutor`, `StateRepository`, `PermissionEngine`, `ContextBuilder`, and `Verifier`. No tool may mutate orchestrator state directly.

Recommended boundaries:

- `contracts`: stable value objects and error/status enums;
- `runtime`: loop and plan scheduling;
- `models`: optional provider adapters, mock gateway, registry, and routing;
- `channels`: optional inbound/outbound adapters and normalized message contracts;
- `tools`: registry, validation, execution envelopes;
- `permissions`: policy, guards, approvals;
- `context`: budget, selection, compaction, artifacts;
- `memory`: lifecycle, retrieval, conflict, retention;
- `sessions`: repositories, checkpoints, rewind;
- `skills`: index, selector, lazy loader;
- `hooks`: event bus, ordering, failure behavior;
- `subagents`: bounded delegation and merge;
- `mcp`: optional connection lifecycle and tool adaptation;
- `verification`: deterministic verifier and eval bridge;
- `telemetry`: redacted logs, traces, metrics, audit;
- `config`: schema, defaults, validation, provenance.

## State machine

The minimum run states are:

`created → planning → running ↔ waiting_approval → verifying → completed`

Terminal alternatives are `failed` and `cancelled`. Persist state transitions atomically with an append-only event or audit record. Reject illegal transitions. A resumed run starts from a durable checkpoint, never from model recollection.

## Core contracts

Use `schemas/agent-state.schema.json` as a language-neutral baseline. Add typed contracts for:

- plan and step dependency graph;
- messages and observations with artifact references;
- model profile and token/cost usage;
- tool request/result/error and side-effect metadata;
- permission decision and approval receipt;
- checkpoint version and configuration fingerprint;
- verification assertions and evidence;
- failure category, retryability, and operator action.

## Control plane versus data plane

The control plane stores configuration, policy, tool/skill catalogs, model profiles, routing, feature flags, and eval definitions. The data plane handles user messages, tool inputs/outputs, artifacts, memory, sessions, and telemetry. Give them separate authorization and retention policies. Configuration changes need provenance, validation, rollout, and rollback.

A browser control plane is still part of the execution product, not the build-time
Agent Factory. The Factory may generate its contracts and source overlay, but only a
later, explicitly authorized delivery task may install, expose, migrate, or deploy it.

## Synchronous and asynchronous work

Use synchronous execution for short interactive steps. Use durable jobs for long research, browser automation, batch evaluation, and fan-out subagents. Durable jobs need idempotency keys, leases, heartbeats, cancellation, checkpointing, retry policy, dead-letter handling, and reconciliation after worker loss.

## Failure taxonomy

Normalize failures into validation, authorization, approval, model transient, model permanent, tool transient, tool permanent, timeout, cancellation, budget exhausted, no progress, persistence conflict, dependency outage, verification failure, and internal invariant. Retry only categories explicitly marked retryable and always within total budgets.

## Configuration precedence

Resolve defaults → environment profile → tenant → user → agent → session → run override. Deny policy and hard safety caps cannot be weakened by lower scopes. Record the effective configuration fingerprint in every run and checkpoint. Never log raw secret values.

Resolve optional adapter selections from `config/integrations.config.json`. Missing or `none` Channel/MCP selections and a development/test `mock` provider are valid. Instantiate only selected adapters; an absent adapter must not make core module construction fail.

## Architecture acceptance

Architecture passes only when:

- public contracts and dependency direction are visible in code;
- safety and cancellation cannot be bypassed through alternate adapters;
- all persisted records carry tenant/run scope;
- model, tools, storage, and clocks can be replaced in tests;
- failures are structured and observable;
- resumption, idempotency, and migrations are defined;
- an end-to-end trace connects request, decisions, tool calls, evidence, and final result.
