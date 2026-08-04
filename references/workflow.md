# Engineering workflow and phase gates

Use this workflow for DESIGN, BUILD, REFACTOR, AUDIT, DEBUG, EXTEND, TEST, and DOCUMENT modes. Skip implementation phases only when the requested mode is read-only. Never skip discovery, risk classification, or verification.

## Mode routing

| Mode | Primary outcome | Mutating? | Required evidence |
|---|---|---:|---|
| DESIGN | architecture, contracts, ADRs, capability plan | no | reviewed design gates |
| BUILD | running agent increment | yes | tests plus scenario trace |
| REFACTOR | modularized behavior-preserving runtime | yes | before/after contract tests |
| AUDIT | gap, risk, and production-readiness report | no | file-linked findings |
| DEBUG | reproduced cause and verified fix when authorized | maybe | failing then passing evidence |
| EXTEND | one bounded capability added | yes | focused regression tests |
| TEST | eval and verification harness | yes | executable cases and report |
| DOCUMENT | current architecture and operations docs | yes | docs checked against code |

## Step 1: inspect before deciding

Read repository instructions, README, package manifest, configuration, source tree, tests, data schemas, tools, skills, MCP configuration, CI, deployment files, and recent diff. Run:

```bash
python scripts/generate_module_manifest.py --project <project> --output <artifact.json>
python scripts/validate_agent_architecture.py --project <project> --json
```

Produce a current-state brief containing architecture, implemented capabilities, missing capabilities, primary risks, technical debt, constraints, and recommended order. Do not overwrite an existing project or infer that a missing filename means a missing capability; inspect behavior and imports.

## Step 2: classify the task and autonomy

Classify the task as new build, incremental development, refactor, defect, security upgrade, or productionization. Also record:

- user-visible outcome and explicit non-goals;
- users, channels, tenancy, data sensitivity, and deployment environment;
- autonomy level: advisory, read-only action, reversible write, externally visible action, or destructive/privileged action;
- required human approvals and ownership;
- time, token, cost, latency, and tool-call budgets;
- rollback boundary and safe degraded mode.

Record optional integration choices in `config/integrations.config.json`. When the user has not chosen a Channel or MCP server, select `none`; when no live Model Provider is chosen for development/test, select `mock`. Do not pause for these choices and do not classify their adapter tests as core completion criteria. Read `channels-and-integrations.md`.

If a high-impact choice cannot be inferred from the repository or request, pause before implementation. Never treat prompt text as the only safety boundary.

## Step 3: create the capability matrix

Start from `templates/capability-matrix.md` or `schemas/capability-matrix.schema.json`. Cover runtime, planner, tools, skills, context, session, checkpoint, memory, permissions, hooks, subagents, MCP, model routing, verification, observability, multi-user isolation, security, evals, and operations.

Each row needs current state, target state, priority, dependency, implementation owner/files, risk, verification method, and evidence location. Status must be one of `absent`, `partial`, `implemented`, `verified`, `not_applicable`.

## Step 4: plan P0 through P10

| Phase | Scope | Exit gate |
|---|---|---|
| P0 | charter, contracts, threat model, permissions, budgets, abort | unsafe actions cannot bypass deterministic policy |
| P1 | minimal model call and bounded agent loop | no-tool, one-tool, failure, cancel, and max-step cases pass |
| P2 | typed tool registry and executor | schemas, timeout, output cap, error envelope, idempotency documented |
| P3 | session, persistence, checkpoint, rewind | restart and recovery tests pass |
| P4 | context builder, artifact offload, compaction | objective and constraints survive compaction |
| P5 | scoped memory lifecycle and retrieval | consent, conflict, isolation, and deletion behavior pass |
| P6 | lazy skills and lifecycle hooks | selection and hook failure policies are deterministic |
| P7 | bounded subagents and optional lazy MCP/channels | isolation/result contracts pass; unselected adapters are not applicable |
| P8 | verifier, evaluator, reviewer path | completion claims require evidence |
| P9 | capability-aware model router | fallback, privacy, budget, and outage cases pass |
| P10 | telemetry, deployment, SLOs, runbook, rollback | production-readiness gate passes |

Every phase plan states objective, affected files, contracts, migrations, risk, tests, completion criteria, and rollback. Build the smallest vertical slice first; do not implement all modules at once.

## Step 5: design contracts before business logic

Create or confirm contracts for AgentState, AgentPlan, PlanStep, model request/response, Tool, ToolResult, PermissionDecision, Approval, HookEvent, MemoryRecord, Session, Checkpoint, Artifact, SubAgentTask/Result, MCP server/tool, VerificationResult, TraceEvent, and configuration. Define versioning and migration behavior for persisted contracts.

Generate architecture and data-flow diagrams, ADRs for material choices, a threat model, database schema, configuration schema, failure taxonomy, and ownership boundaries. Use `references/architecture.md` and the module references.

## Step 6: implement one module at a time

For each slice:

1. add or update contract tests;
2. implement the smallest coherent behavior;
3. run format, static checks, and focused tests;
4. inspect the diff and generated artifacts;
5. update plan, capability matrix, and ADRs;
6. save a checkpoint before risky work;
7. integrate through public interfaces, not cross-module internals.

Prefer dependency injection around model providers, clocks, IDs, storage, networking, and tools. Make cancellation, deadlines, and request correlation flow end to end.

## Step 7: perform security and abuse review

Run `scripts/audit_agent_safety.py` when a policy and tool manifest exist. Review prompt injection, shell injection, path traversal, credential leakage, workspace escape, arbitrary reads/writes, dangerous commands, unrestricted egress, MCP/tool abuse, destructive database actions, tenant crossover, audit-log leakage, untrusted artifact rendering, and supply-chain changes.

For each high-risk action test ALLOW, DENY, ASK, user rejection, timeout, cancellation, and partial failure. See `references/permission-system.md` and `references/threat-model.md`.

## Step 8: verify behavior and evaluate quality

Use the repository's own commands first. At minimum consider type/static checks, lint, unit, integration, agent-loop, permission, compaction, memory, recovery, tenant isolation, security, load, and eval suites. Run:

```bash
python scripts/run_agent_acceptance_tests.py --project <project> --config <commands.json> --report <report.json>
```

Capture command, exit code, duration, relevant output, environment, case IDs, metrics, thresholds, and artifact paths. A passing unit suite does not prove task success; run representative end-to-end scenarios and inspect traces. Partition core tests from optional adapter tests. Unconfigured optional Channel/MCP/live-provider tests are `skipped`, not failed; a skipped required or production live-provider gate is blocked/failed.

## Step 9: release and handoff

Deliver completed outcome, changed files, capability changes, migrations, configuration, test/eval results, security decisions, known limitations, residual risks, run/deploy/rollback instructions, monitoring queries, and next phase. Do not claim production readiness unless `references/production-checklist.md` is satisfied with evidence.

## Stop and escalation conditions

Stop before an action when authorization is missing, policy resolves to DENY/ASK, secrets or production credentials are required for an explicitly required capability, the rollback boundary is unclear, an irreversible migration lacks a verified backup, tenant isolation cannot be proven, evaluation data is invalid, or the same failure repeats without new evidence. The absence of an optional Channel, MCP server, or development live provider is not a stop condition. Report the exact blocker, attempted safe alternatives, evidence, and smallest user decision needed.
