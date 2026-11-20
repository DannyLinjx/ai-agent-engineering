# Reference architecture

Design the runtime as replaceable modules connected by explicit contracts. The model proposes; deterministic code validates, authorizes, executes, persists, and verifies.

## Layer model

1. **Interface** — optional CLI, native graphical CLI client, web, API, IDE, Telegram, Feishu/Lark, WeCom/企业微信, Slack, Discord, Teams, email, webhook, or automation adapters. Normalize identity, channel, locale, attachments, cancel signal, and response streaming. A core runtime may have no registered channel.
2. **Identity, tenant, session, workspace** — authenticate, resolve scopes, enforce workspace roots, and open or resume a session.
3. **Orchestrator** — classify intent, select mode, create a plan, schedule steps, maintain state, and apply termination rules.
4. **Context, memory, skill selection** — build only the task-relevant context under a measured token budget.
5. **Model query engine** — select provider/model, stream, validate structured output, use the existing explicitly bounded transient-failure policy, honor cancellation/deadlines, and meter cost.
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

For durable Memory, follow `../assets/memory-platform.mmd`: each record class has one canonical authority with reviewed storage, encryption and consent rules, while FTS, vector, graph, and framework integrations consume lifecycle
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

Terminal alternatives include `failed`, `cancelled` and explicitly incomplete `partial`. Products with interactive control additionally model waiting_input, pause_requested/paused/resuming and cancel_requested as needed; an accepted control request is not its confirmed state. Do not make every implementation adopt identical enum names. Persist state transitions atomically with an append-only event or audit record. Reject illegal transitions. A resumed run starts from a durable checkpoint, never from model recollection.

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

## Native clients and runtime ownership

A native conversation client is a graphical projection of the selected CLI/Harness, not a terminal emulator or a reason to add HTTP/WebView. CLI and GUI use the same identity, Runtime, policy, model/tool gateways and canonical persistence. A local process transport carries typed request/response/event correlation, durable snapshots/cursors and cancellation; the client does not execute Agent work. See [native-cli-client.md](native-cli-client.md).

Find each existing owner before adding a prompt writer, planner/router, memory system, fallback, summary or retry layer. A wrapper such as create_agent must not be used as one LLM call inside another loop exposing the same tools. Advisory routers and governed child subgraphs inherit the parent's scope and cumulative budgets; they do not create a parallel control plane.

Run state, canonical messages/artifacts, retrieval projections, long-term preferences and learned policy have different owners/lifecycles. Source selection confirms a precise session scope; each Run pins it. Authorize before cache/derived-body reads and final delivery, including revocation/Forget. Do not force a storage migration just because a reference scaffold uses a database.

## Capability facts and retirement

Use [capability-readiness.md](capability-readiness.md) to distinguish registration, dependencies, configuration, authority, probe, host binding, model invocation and actual product verification. Standby is neither absent nor currently running. A retired backend is persistently disabled: old probes/caches, recovery jobs or installers cannot revive it; unrelated tools remain independent. Missing isolation never silently falls back to host execution.
