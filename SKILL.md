---
name: ai-agent-engineering
description: Design, build, refactor, debug, test, and deliver tool-using AI agent systems. Use for governed runtimes, CLI/native/browser clients, model and tool integrations, scoped sources and memory, recovery, controlled prompt learning, evaluation, and operations; preserve the project architecture and authorization.
license: MIT
---

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
- **FACTORY** — convert enterprise requirements into a governed Agent Blueprint, deterministic Build Recipe, candidate project, evidence bundle, and human release checklist.

For a read-only request, do not mutate code or external systems. For build/change requests, implement and verify the requested outcome. Follow repository instructions and preserve unrelated user changes.

## Current contract and real integration

- Preserve the current user contract, non-goals and superseded decisions. Repository/user instructions override reference packages and Skill defaults; attachments do not grant additional authority.
- Inspect the real source, entry, worker interpreter, configuration and loaded process before changing code. Save scoped beforeimages including untracked files; `git diff` alone is incomplete. Missing paths stay unknown.
- Map interface action → identity/session → Runtime → Registry/permissions → model wire tools → executor → receipt/artifact → tool-result message → client projection. Classes, metadata, copied patches and `design/` templates do not prove host integration.
- Use one governed execution/permission path across selected clients. Do not create a second Runtime/store/auth/model gateway to fit a library. Reuse the existing owner before adding summaries, retries, fallback, routers or memory layers.
- Continue routine work already authorized for the same action, target, data and risk. Ask only for a material missing decision or scope expansion, with the specific reason. Install/download authority does not authorize private-data egress, cloud tracing, shared-service changes or publication. Never evade rejection by changing shell/language, hiding background work or weakening isolation.
- Native/CLI/browser experiences are project choices. Inspect the current user's requirements rather than importing another project's paths, build commands, framework, language, visual style or retired features.

## Learning and publication boundary

When improving this Skill from private development experience, extract general
decision rules and independently synthetic examples. Do not include project names,
local paths, endpoints, screenshots, source, transcripts, architecture snapshots,
project-specific profiles, operational history or identifying combinations of facts.
Removing a name alone is not anonymization. Authorization to update or publish a
Skill covers that Skill's generic content; it does not authorize publishing its
source projects. Project-derived disclosures require separate explicit approval
for the exact content and destination. Before publishing, review the complete
file set, filenames, metadata and diff for that boundary; credential scanning alone
cannot establish publication permission. If a disclosure has already occurred,
stop further disclosure, remediate the current version, and separately assess Git
history and public copies without claiming that a new commit erased them.

## Optional integration rule

Treat Channel adapters, live Model Providers, and MCP servers as independent, user-selectable integrations. Read `references/channels-and-integrations.md` whenever configuring or testing them.

- Do not require the user to choose any Channel or MCP server. Default both to `none`.
- Do not require a live Model Provider for scaffolding, core runtime work, deterministic tests, or offline evals. Default development/test to `mock`.
- Accept Telegram, Feishu, Lark, WeCom/企业微信, WeChat Official Account, Slack, Discord, Microsoft Teams, email, webhook, CLI, web, or API adapters through configuration; never hard-code Telegram as the only channel.
- If an optional integration is unselected, mark its tests `skipped` or `not_applicable`; do not fail the core workflow and do not ask the user to configure it.
- Require a real provider only for a requested live-model acceptance criterion or `production` profile. Channels and MCP remain optional unless the charter explicitly marks them required.
- Store only `secret://`, `env://`, or `vault://` credential references in config. Never request or write raw credentials into project files.

For a new scaffold, create a valid core-only `config/integrations.config.json` and continue when the user makes no selection. For an existing product, preserve its configuration system rather than adding a parallel one. Report selected, skipped, and blocked integrations separately.

## Mandatory workflow

Read `references/workflow.md` and apply its nine steps and stop conditions. In summary:

1. **Inspect before modifying.** Read instructions, README, manifests, configuration, optional integration selections, source, schemas, tools/skills/MCP, tests, CI/deploy, and diff. Generate a module manifest when useful.
2. **Classify task and autonomy.** Record outcome, non-goals, users/tenancy, data, deployment, side effects, approvals, budgets, rollback, and escalation.
3. **Create a capability matrix.** Assess runtime, planner, tools, skills, context, session/checkpoint, memory, permissions, hooks, subagents, MCP, routing, verification, observability, isolation, security, evals, and operations.
4. **Reuse the authorized phase plan.** Preserve user-supplied phases and acceptance IDs. Only when none applies, use P0–P10 as a reference ordering: safety/contracts, reliable state/control, tools, durability, context/memory, extensions, verification and operations. Do not substitute another generic plan for requested implementation.
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

Treat `agents/*` and `host-adapters/*` as optional host metadata. Their absence must not invalidate the core Skill.

Treat the Agent Factory as a build-time control plane and the generated Agent Runtime as the execution plane. The Factory may generate and verify candidates; it never grants high-risk permissions or deploys production without human approval. Read `references/agent-factory.md` for Factory requests.

For Factory requests, normalize three independent profiles before implementation:

- **Experience:** `headless`, `browser_chat`, `operations_console`, or `native_chat`. Read [client-experience](references/client-experience.md), then the browser or [native CLI](references/native-cli-client.md) reference that matches the actual product. Native uses `native_cli` with `stdio`/`local_ipc`; do not add Web to fit a template. Generated manifests distinguish planned clients from runnable implementations.
- **Memory:** disabled or `local`, `hybrid`, or `enterprise`. Read `references/memory-deployment.md` with `references/memory-system.md`. Keep one authoritative owner per record class and treat keyword, vector, graph, and framework integrations as lifecycle-governed projections. Preserve existing encrypted-file/scoped-Markdown designs; a canonical authority need not be a single physical database. File-store Factory options are planned adapters, not generated persistence implementations.
- **Delivery:** `plan_only`, `guided_install`, or `end_to_end`. This selects the requested engagement, not authority. The Factory still cannot install, migrate live data, expose services, or deploy.

Legacy Blueprints without these sections remain valid and normalize to headless, disabled local Memory, and plan-only delivery.

## Module routing

Load only the references required by the task:

| Need | Read |
|---|---|
| create an enterprise Agent from a Blueprint; Agent creates Agent | `references/agent-factory.md` |
| conversation UI, auth, Settings, IME, rich messages and client state | [client-experience](references/client-experience.md) |
| native CLI client, stdio/IPC, actual launcher and worker lifecycle | [native-cli-client](references/native-cli-client.md) |
| real capability wiring, probes, standby, disable and retirement | [capability-readiness](references/capability-readiness.md) |
| scoped source selection, Reader, program batches, evidence/coverage | [document-source-pipelines](references/document-source-pipelines.md) |
| deterministic Prompt, feedback jobs, optimizer, review/CAS/revoke | [prompt-policy-learning](references/prompt-policy-learning.md) |
| project paths, sparse disks/container dependencies and exact cleanup | [runtime-storage-operations](references/runtime-storage-operations.md) |
| browser chat, operations console, React/FastAPI control plane | `references/browser-experience.md` |
| loop, planner, budgets, retry, cancellation, completion | `references/agent-runtime.md` |
| tool contract, registry, command/path/network safety | `references/tool-system.md` |
| skill discovery, selection, scopes, scripts | `references/skill-system.md` |
| token budgets, artifact offload, compaction, injection boundary | `references/context-management.md` |
| durable memory, consent, retrieval, conflict, deletion | `references/memory-system.md` |
| local SQLite Memory, enterprise adapters, migration/deployment | `references/memory-deployment.md` |
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
2. before each iteration enforce cancel, deadline, configured steps/replans, tokens/cost, failures, repeated actions, and progress; an explicit `0=uncapped count` never disables the independent safeguards;
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

Stop on missing authority, unclear isolation, invalid evidence, policy DENY/ASK or repeated failure without a new hypothesis. An explicitly authorized destructive disposal requires an exact scope and honest data-loss boundary; do not silently preserve another giant copy or invent a rollback. Continue unaffected authorized work.

## Build and scaffold

For an existing project, keep its language and framework. Use the Python and TypeScript templates only as architectural references when the repository uses another language; do not migrate languages because of template availability.

For a new project, choose a runnable reference scaffold or the language-neutral `generic` scaffold:

```bash
python scripts/scaffold_agent_project.py --language typescript --name "My Agent" --target ./my-agent
python scripts/scaffold_agent_project.py --language python --name "My Agent" --target ./my-agent
python scripts/scaffold_agent_project.py --language generic --name "My Agent" --target ./my-agent
```

The `generic` scaffold copies language-neutral schemas, configuration, architecture guidance, and a contract test plan without generating Python or TypeScript source code.

For a governed Agent Factory flow, plan before applying:

```bash
python scripts/create_agent_from_blueprint.py --blueprint <blueprint.json> --target <project> --plan <recipe.json>
python scripts/create_agent_from_blueprint.py --blueprint <blueprint.json> --target <project> --apply --report <report.json>
```

`--plan` never mutates the target. `--apply` refuses blockers and non-empty targets, generates candidate artifacts, and stops at human release approval.

Use [native-local-agent-blueprint.json](examples/native-local-agent-blueprint.json) for native/stdio plus planned file-memory surfaces, `examples/local-memory-agent-blueprint.json` for the local Browser + SQLite path and `examples/browser-enterprise-agent-blueprint.json` for the governed operations-console + PostgreSQL plan. Applying a supported Python Browser profile composes the `browser-react-fastapi` overlay without installing dependencies or starting services.

Then copy and complete `templates/agent-charter.md`, `templates/capability-matrix.md`, `templates/threat-model.md`, `templates/agent-config.yaml`, `templates/permission-policy.yaml`, and `templates/acceptance-test-plan.md`. Use `schemas/` as language-neutral configuration/state/tool/eval/trace/readiness contracts. The scaffolds are intentionally minimal: add storage, migrations, telemetry, skills, MCP, and business tools through their interfaces rather than weakening boundaries.

Native GUI and file-store adapters remain planned surfaces in current Factory output. Blueprint `max_steps=0` is planning-only for the reference scaffolds: apply rejects before writing until a governed Runtime supplies the required independent safeguards.

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
python scripts/validate_experience_manifest.py --manifest <project>/factory/experience-manifest.json --json
python scripts/validate_memory_manifest.py --manifest <project>/factory/memory-manifest.json --json
python scripts/run_agent_acceptance_tests.py --project <project> --config <commands.json> --report <report.json>
python scripts/validate_skill_structure.py --skill . --json
```

The architecture validator is evidence discovery, not formal proof. Confirm findings by reading actual contracts and call paths. The safety audit is conservative and requires human triage.

## Verification minimums

Select checks proportional to the changed behavior and release risk. Use relevant static/compile, focused unit, integration and actual-product E2E evidence; do not run unrelated suites merely to satisfy a fixed checklist. Critical agent releases cover:

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

## Final product evidence and convergence

Requested/accepted control is not confirmed state. Pause/resume/Stop act on the same durable Run; views, new chats and transport disconnects do not cancel it. Epoch/sequence/idempotency fences reject duplicate finals and late results. Source revocation also invalidates cached fragments, summaries and derived answers before content reads and delivery.

Configuration saved ≠ dependency present ≠ probe verified ≠ host bound ≠ model called ≠ product E2E passed. Capability descriptions and model schemas use actual scoped snapshots. Persistent retirement fences catalog, execution, probes, recovery and installation/provisioning; stale Ready records cannot resurrect a retired backend, and missing isolation cannot fall back to host execution.

Verify source → build → package → actual user launcher → loaded worker → observed behavior after the final relevant change. Cache/source-only success is not launcher acceptance. Keep component, independent tool, Runtime, natural-language E2E, GUI and OS isolation results separate. Missing/blocked/unverified/partial are not pass; reference tests are not main-product acceptance.

After two attempts at the same failure without new evidence, change the hypothesis or method using the installed API/source/docs. Do not keep adjusting UI offsets, timeouts, model parameters or permissions. Once affected gates pass with no new changes or unresolved material concerns, stop repeating broad/stress tests.

Record real command/subprocess exits, fingerprints, artifact bytes/hashes, physical RPC vs logical operations, coverage, token/cache/prefill/decode/latency and unknowns. Small samples do not establish stable P95 or statistical improvement. Clean only exact owned inactive QA/cache objects after their processes close, retaining compact evidence. No publication/upload without project-and-destination authority.

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
