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

Read the relevant repository instructions, current user contract, README, manifests, non-secret configuration shape, source, tests and dirty/untracked state. Separate superseded plans from current requirements; do not inspect private payloads or credentials merely for discovery. Use these helpers when they add evidence:

```bash
python scripts/generate_module_manifest.py --project <project> --output <artifact.json>
python scripts/validate_agent_architecture.py --project <project> --json
```

Produce a scoped current-state brief and source-to-integration map: actual entry/loaded process, worker interpreter, configuration persistence/injection, identity, Runtime, Registry, permission filters, model-visible schema, executor, tool receipts returned to the model, and client projection. Include named functions/tests where observed; leave missing evidence unknown. Save beforeimages and hashes for affected tracked and untracked files, not only a git diff. Do not overwrite an existing project or infer that a missing filename means a missing capability; inspect behavior and imports.

## Step 2: classify the task and autonomy

Classify the task as new build, incremental development, refactor, defect, security upgrade, or productionization. Also record:

- user-visible outcome and explicit non-goals;
- users, channels, tenancy, data sensitivity, and deployment environment;
- autonomy level: advisory, read-only action, reversible write, externally visible action, or destructive/privileged action;
- required human approvals and ownership;
- time, token, cost, latency, and tool-call budgets;
- rollback boundary and safe degraded mode.

For a new scaffold record optional integration choices in `config/integrations.config.json`; for an existing product reuse its configuration owner. When the user has not chosen a Channel or MCP server, select `none`; when no live Model Provider is chosen for development/test, select `mock`. Do not pause for these choices and do not classify their adapter tests as core completion criteria. Read `channels-and-integrations.md`.

For Factory work, also record the Experience (`headless`, `browser_chat`, or
`operations_console`), Memory (`disabled`, `local`, `hybrid`, or `enterprise`), and
Delivery (`plan_only`, `guided_install`, or `end_to_end`) profiles. Read
`client-experience.md` and the selected native/browser reference, plus `memory-deployment.md`. These selections define the
candidate and implementation plan; they do not authorize dependency installation,
credential configuration, live-data migration, network exposure, or deployment.

Maintain a scope/authorization ledger: action, target, data, risk, expiry and evidence of authority. Continue unchanged authorized local work without repeated confirmations. Installation is not permission to transmit data, enable tracing, publish, reboot a shared service or broaden host access. If a material choice remains unknown, ask a concise question while continuing independent work. Never treat prompt text as the only safety boundary.

## Step 3: create the capability matrix

Start from `templates/capability-matrix.md` or `schemas/capability-matrix.schema.json`. Cover runtime, planner, tools, skills, context, session, checkpoint, memory, permissions, hooks, subagents, MCP, model routing, verification, observability, multi-user isolation, security, evals, and operations.

Each row needs current state, target state, priority, dependency, implementation owner/files, risk, verification method, and evidence location. Status must be one of `absent`, `partial`, `implemented`, `verified`, `not_applicable`.

## Step 4: preserve the user plan; use P0–P10 only as a fallback

If the user supplied stages, IDs, design baselines or acceptance gates, execute those instead. Map necessary safety/compatibility gaps into that plan without replacing it or delivering another generic plan. For an otherwise unplanned build, the following is a dependency ordering, not a demand to implement every module.

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

For any graphical client, add Principal, Command, Job, safe Run Event, event cursor, approval fingerprint and projection contracts. Select SSE/WebSocket only for a selected browser product; native CLI clients use their existing stdio/IPC. Read `client-experience.md`. When Memory is
selected, add canonical-store ownership, policy decision, lifecycle event, index
outbox, export/import, migration, and rollback contracts before adapter code.

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

Use the repository's own commands first and select checks for changed behavior and risk. Consider type/static checks, lint, unit, integration, agent-loop, permission, compaction, memory, recovery, tenant isolation, security, load, and eval suites. Run:

```bash
python scripts/run_agent_acceptance_tests.py --project <project> --config <commands.json> --report <report.json>
```

Capture the real subprocess exit (not tail/tee status), duration, safe output, environment, case IDs, versions, metrics, thresholds and actual artifacts. Freeze input bytes, source/config/profile/tool/policy identities and cache state for comparisons. After the final relevant change verify the actual main product/launcher and loaded worker; reference examples, offline templates and alternate mini-Demos cannot satisfy product E2E. Keep component, standalone tool, real Runtime, natural-language E2E, GUI and isolation evidence separate. A passing unit suite does not prove task success; run representative end-to-end scenarios and inspect traces. Partition core tests from optional adapter tests. Unconfigured optional Channel/MCP/live-provider tests are `skipped`, not failed; a skipped required or production live-provider gate is blocked/failed.

After two unsuccessful adjustments without new evidence, change the hypothesis or method using the installed API/source/docs. Once affected checks pass and no new edits/failures/material unknowns remain, converge rather than repeating broad or stress suites. Preserve prior failures and report unresolved/blocked/skipped distinctly.

## Step 9: release and handoff

Deliver completed outcome, changed files, capability changes, migrations, configuration, test/eval results, security decisions, known limitations, residual risks, run/deploy/rollback instructions, monitoring queries, and next phase. Include safe scope-specific before/after screenshots when the UI changed, final source/build/package/loaded identities, exact rollback/data-loss boundaries, and whether the running instance loaded the final change. Close owned processes before deleting exact disposable QA/cache targets; retain compact evidence outside the product, not user data. Never upload/publish without project-and-destination authority. Do not claim production readiness unless `references/production-checklist.md` is satisfied with evidence.

## Stop and escalation conditions

Stop before an action when authorization is missing, policy resolves to DENY/ASK, secrets or production credentials are required for an explicitly required capability, the rollback boundary is unclear, an irreversible effect lacks explicit disposal authority or an adequate recovery boundary, tenant isolation cannot be proven, evaluation data is invalid, or the same failure repeats without new evidence. The absence of an optional Channel, MCP server, or development live provider is not a stop condition. Report the exact blocker, attempted safe alternatives, evidence, and smallest user decision needed.

For user-authorized disposal, record exact objects and irreversible data loss; do not create an unwanted giant backup or pretend a code rollback restores deleted data. Persistent retirement must fence recovery/installers as well as execution. A tool/OS permission failure is not approval to change shells, run hidden work, weaken isolation or manipulate system permission stores.
