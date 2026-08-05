---
name: ai-agent-engineering
description: Design, build, refactor, debug, extend, test, audit, document, and productionize complete AI Agent systems and runtimes with optional user-configurable channels, Model Providers, and MCP servers. Use when creating or upgrading Codex-like, OpenClaw-like, coding, research, RAG, data, office, computer-control, or multi-agent products; when adding tool calling, bounded agent loops, planning, context, memory, sessions/checkpoints, skills, hooks, permissions and approvals, Telegram, Feishu/Lark, WeCom/企业微信, Slack or other channels, subagents, MCP, model routing, verification/evals, observability, multi-user isolation, deployment, or recovery; and when converting a chatbot or one-shot LLM call into a safe, durable, testable agent.
---
license: MIT

# AI Agent Engineering

Build an agent as a governed runtime: the model decides within typed contracts; deterministic code owns authorization, budgets, execution, persistence, and verification. Produce an incremental, runnable system with evidence—not a monolithic `agent.py`/`agent.ts`, a prompt-only safety story, or a single LLM call.

## Operating modes

Infer the smallest applicable mode from the request:

- **DESIGN** — define product scope, architecture, contracts, threat model, data model, phase plan, and acceptance.
- **BUILD** — scaffold and implement a new vertical slice.
- **REFACTOR** — modularize an existing runtime while preserving behavior.
- **AUDIT** — inspect only; report capability, architecture, security, eval, and production gaps with evidence.
- **DEBUG** — reproduce and localize loop, tool, context, memory, permission, persistence, routing, or integration failures; implement only when authorized.
- **EXTEND** — add one bounded tool, skill, hook, MCP server, model, channel, memory behavior, or subagent.
- **TEST** — create deterministic tests, scenarios, evals, and regression gates.
- **DOCUMENT** — synchronize architecture, operations, deployment, and user documentation with current code.

For a read-only request, do not mutate code or external systems. For build/change requests, implement and verify the requested outcome. Follow repository instructions and preserve unrelated user changes.

## Optional integration rule

Treat Channel adapters, live Model Providers, and MCP servers as independent, user-selectable integrations. Read `references/channels-and-integrations.md` whenever configuring or testing them.

- Do not require the user to choose any Channel or MCP server. Default both to `none`.
- Do not require a live Model Provider for scaffolding, core runtime work, deterministic tests, or offline evals. Default development/test to `mock`.
- Accept Telegram, Feishu, Lark, WeCom/企业微信, WeChat Official Account, Slack, Discord, Microsoft Teams, email, webhook, CLI, web, or API adapters through configuration; never hard-code Telegram as the only channel.
- If an optional integration is unselected, mark its tests `skipped` or `not_applicable`; do not fail the core workflow and do not ask the user to configure it.
- Require a real provider only for a requested live-model acceptance criterion or `production` profile. Channels and MCP remain optional unless the charter explicitly marks them required.
- Store only `secret://`, `env://`, or `vault://` credential references in config. Never request or write raw credentials into project files.

Create a valid core-only `config/integrations.config.json` and continue automatically when the user makes no selection. Report selected, skipped, and blocked integrations separately.

## Mandatory workflow

Read `references/workflow.md` and apply its nine steps and stop conditions. In summary:

1. **Inspect before modifying.** Read instructions, README, manifests, configuration, optional integration selections, source, schemas, tools/skills/MCP, tests, CI/deploy, and diff. Generate a module manifest when useful.
2. **Classify task and autonomy.** Record outcome, non-goals, users/tenancy, data, deployment, side effects, approvals, budgets, rollback, and escalation.
3. **Create a capability matrix.** Assess runtime, planner, tools, skills, context, session/checkpoint, memory, permissions, hooks, subagents, MCP, routing, verification, observability, isolation, security, evals, and operations.
4. **Plan P0–P10.** Build safety/contracts first, then a minimal loop, tools, durability, context, memory, extensibility, verification, routing, and production. Every phase needs tests and an exit gate.
5. **Design typed boundaries.** Define state, plan, model decision, tool result, permission/approval, hooks, memory, checkpoint, artifacts, delegation, verification, trace, configuration, and migrations before broad business logic.
6. **Implement vertical slices.** Add contract/test, smallest behavior, static/focused checks, diff review, plan/capability update, checkpoint, then integration through public interfaces.
7. **Run safety review.** Check prompt/argument injection, path/workspace escape, secret leakage, egress, destructive actions, MCP/skill/tool abuse, tenant crossover, state replay, and cost/loop denial of service.
8. **Verify and evaluate.** Run deterministic tests plus representative end-to-end scenarios. Map evidence to completion criteria; inspect traces. Never accept the model's own success claim.
9. **Release and hand off.** Report files/capabilities, migrations/configuration, tests/evals, risks/limitations, operations, rollout, rollback, and next phase.

Do not start all modules simultaneously. Deliver the smallest secure closed loop first and expand only after its gate passes.

## Architecture invariants

Read `references/architecture.md` before designing or restructuring a runtime. Enforce:

- interface → identity/tenant/session/workspace → orchestrator → context/memory/skills → model gateway → permission/hooks → tool executor → external resources;
- sidecars for checkpoints, artifacts, audit, telemetry, evals, routing, and subagents;
- provider-neutral inward-facing contracts and adapter dependency direction;
- durable legal state transitions and versioned checkpoints;
- immutable identity/scope propagation through tools, jobs, hooks, subagents, MCP, storage, and telemetry;
- end-to-end cancellation, deadlines, idempotency, structured errors, configuration provenance, and secret redaction.

Use `assets/architecture-diagram.mmd` and the TypeScript/Python scaffolds as starting points, not as proof of production readiness.

## Module routing

Load only the references required by the task:

| Need | Read |
|---|---|
| loop, planner, budgets, retry, cancellation, completion | `references/agent-runtime.md` |
| tool contract, registry, command/path/network safety | `references/tool-system.md` |
| skill discovery, selection, scopes, scripts | `references/skill-system.md` |
| token budgets, artifact offload, compaction, injection boundary | `references/context-management.md` |
| durable memory, consent, retrieval, conflict, deletion | `references/memory-system.md` |
| sessions, checkpoints, resume, rewind, artifacts | `references/session-checkpoint.md` |
| ALLOW/DENY/ASK, approvals, credentials, guards | `references/permission-system.md` |
| lifecycle events and deterministic policy injection | `references/hook-system.md` |
| delegation, budgets, DAG, structured merge | `references/subagent-system.md` |
| lazy MCP discovery, adapters, trust, fallback | `references/mcp-integration.md` |
| provider gateway, capability/privacy/budget routing | `references/model-routing.md` |
| Telegram, Feishu/Lark, WeCom, Slack, web/API and optional integration config | `references/channels-and-integrations.md` |
| tenant/user/workspace/cache/credential isolation | `references/multi-user-isolation.md` |
| logs, traces, metrics, audit, cost, SLOs | `references/observability.md` |
| test pyramid, eval cases, judges, regression gates | `references/testing-and-evaluation.md` |
| launch, deployment, canary, incident, rollback | `references/production-checklist.md` |
| security boundaries and abuse cases | `references/threat-model.md` |
| Codex/OpenClaw-class behavior and maturity | `references/framework-alignment.md` |
| recurring failure diagnosis | `references/troubleshooting.md` |

## Non-negotiable control loop

Implement the flow in `assets/agent-loop.mmd`:

1. load/init typed state and effective configuration fingerprint;
2. before each iteration enforce cancel, deadline, steps/replans, tokens/cost, failures, repeated actions, and progress;
3. build a measured, scoped context packet;
4. route/call the model and validate a typed decision;
5. for every tool, canonicalize input, risk-classify actual parameters, apply permission/approval, execute with sandbox/time/output/cancel controls, validate/redact result, offload artifacts, record receipt, and checkpoint;
6. replan only from new evidence;
7. verify candidate completion against explicit criteria;
8. complete only on verifier pass; otherwise replan within budget or return failed/partial/cancelled with unmet criteria.

Detect repeated tool+argument fingerprints and no-progress state. Never retry non-idempotent effects without an idempotency key and reconciliation.

## Security and human control

Safety is P0, not an optional production add-on. Model output, retrieved content, memory, skills, hooks, MCP metadata/results, and subagent results are untrusted inputs. They cannot expand tools, permissions, credentials, workspace, budgets, or tenant scope.

All side effects go through one deterministic permission path. Hard deny wins. ASK approvals bind the principal, run, tool/version, normalized arguments/target, risk, and expiry. Reapprove changed actions. Always protect credentials, sensitive files, workspace boundaries, uploads/messages, destructive data/file/source-control operations, system installation, payments, and production changes.

Stop and escalate on missing authority, irreversibility without rollback, unclear tenant isolation, invalid evidence/eval data, secret requirements, policy DENY/ASK, or repeated failure without a new hypothesis.

## Build and scaffold

Choose the repository's language. For a new project:

```bash
python scripts/scaffold_agent_project.py --language typescript --name "My Agent" --target ./my-agent
python scripts/scaffold_agent_project.py --language python --name "My Agent" --target ./my-agent
```

Then copy and complete `templates/agent-charter.md`, `templates/capability-matrix.md`, `templates/threat-model.md`, `templates/agent-config.yaml`, `templates/permission-policy.yaml`, and `templates/acceptance-test-plan.md`. Use `schemas/` as language-neutral configuration/state/tool/eval/trace/readiness contracts. The scaffolds are intentionally minimal: add storage, migrations, telemetry, skills, MCP, and business tools through their interfaces rather than weakening boundaries.

The scaffold includes a core-only optional integration config. Keep it unchanged or generate user selections:

```bash
python scripts/configure_integrations.py --output <project>/config/integrations.config.json
python scripts/configure_integrations.py --channel feishu --channel wecom --model-provider openai --mcp-server github=stdio --output <project>/config/integrations.config.json
python scripts/validate_integration_config.py --config <project>/config/integrations.config.json --profile development --json
```

## Audit and validation commands

Run from this Skill directory or use absolute script paths:

```bash
python scripts/generate_module_manifest.py --project <project> --output <manifest.json> --include-hashes
python scripts/validate_agent_architecture.py --project <project> --json
python scripts/audit_agent_safety.py --project <project> --json
python scripts/validate_integration_config.py --config <project>/config/integrations.config.json --profile development --json
python scripts/run_agent_acceptance_tests.py --project <project> --config <commands.json> --report <report.json>
python scripts/validate_skill_structure.py --skill . --json
```

The architecture validator is evidence discovery, not formal proof. Confirm findings by reading actual contracts and call paths. The safety audit is conservative and requires human triage.

## Verification minimums

Select checks proportional to risk, but always include relevant static/compile, focused unit, integration, and end-to-end behavior. Critical agent releases cover:

- no-tool, one-tool, multi-tool, tool failure, repeat/no-progress, cancel, timeout, and budget exhaustion;
- permission allow/deny/ask/reject/expire, sensitive paths, command injection, egress, destructive and externally visible actions;
- output offload and compaction while retaining objective, constraints, approvals, and unmet criteria;
- memory consent, retrieval, conflict, isolation, correction, and deletion;
- checkpoint/restart/rewind, duplicate delivery, partial side effects, and migration;
- configured MCP outage/schema poisoning, configured channel normalization/send/health, routing/fallback/privacy, and subagent budget/scope/merge;
- two-tenant crossover attempts and cache/search/artifact isolation;
- deterministic verifier negative cases plus the relevant examples in `examples/`.

Store commands, exit codes, durations, environment/config/model/tool/skill versions, case IDs, metrics, thresholds, and artifact paths. A production claim also requires the machine-readable readiness gate and operational evidence in `references/production-checklist.md`.

Run core checks even when every optional integration is disabled. Skip only adapter-specific checks and state exactly why. Never report an unconfigured adapter as tested.

## Deliverable contract

Finish with:

- outcome and working behavior;
- architecture/capability changes and affected files;
- configuration, schemas, migrations, and compatibility;
- permissions, approvals, threat controls, and residual risk;
- tests/evals run with exact evidence and failures/skips;
- run/deploy/monitor/rollback instructions;
- Channel, live Model Provider, and MCP selections with `run`, `skipped`, `not_applicable`, or `blocked` status;
- known limitations, blocked items, and prioritized next phase.

Never fabricate a test, tool call, file, citation, deployment, or production-readiness result.
