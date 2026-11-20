# Testing and evaluation

Testing proves deterministic code behavior; evaluation estimates agent quality on
representative tasks. Select both in proportion to the requested change and its
risks; do not turn a documentation edit into a live-model/product release campaign.

## Test pyramid

1. schema and contract tests;
2. unit tests for policies, budgets, ranking, state transitions, compaction, and error mapping;
3. adapter/tool integration tests with controlled dependencies;
4. runtime scenario tests with scripted/fake models;
5. end-to-end tests in an isolated workspace;
6. security, tenant-isolation, recovery, load, and chaos tests;
7. offline evals and a small monitored online/canary set.

Use fake clocks, IDs, providers, tools, channels, MCP clients, and storage to make core tests deterministic. Live-provider, Channel, and MCP tests are opt-in, budgeted, labeled, and never the only core evidence. When an optional adapter is not selected, record its suite as `skipped`/`not_applicable` without failing the release's core development gate.

## Mandatory runtime cases

No-tool response, one tool, multiple tools, tool failure/recovery, configured count
limits (including an explicitly supported unlimited-count mode with other guards),
repeat/no-progress, cancellation, deadline, token/cost exhaustion, checkpoint/restart,
verification failure/replan and partial irreversible side effect.

Also cover permission, context, memory, session, multi-user, MCP, routing, and subagent cases listed in their references.

Selected Browser profiles additionally cover authentication/logout, CSRF, scoped
object guesses, command idempotency, Worker lease loss, cancellation, safe Event
redaction, SSE reconnect/replay, approval change/expiry/rejection, artifact security,
responsive keyboard interaction, and verified completion. Selected Memory profiles
cover consent/secret rejection, restart persistence, authorization-before-ranking,
conflict/correction, expiry/deletion propagation, deterministic export, index rebuild,
and—when applicable—backup restore and shadow migration comparison.

Selected graphical clients use [client-experience.md](client-experience.md): validate
real authentication, draft/attachment/settings roundtrip, source confirmation/revoke,
Ask User, request-versus-confirmed run controls, replay/late-result deduplication,
themes/focus/IME, content safety/copy/history, long-message/stream interaction and
authorized evidence/download. Adapt rich-message features to the product promise.
Native packaging/stdio and user-entry checks are in
[native-cli-client.md](native-cli-client.md); do not substitute web fixtures.

Capability changes include empty optional extensions, actual model wire schemas,
permission/config version invalidation, standby behavior, and retired tools staying
disabled through execution/probe/recovery/install. A replacement test for a retired
feature verifies denial/no recreation, not its former successful execution.

## Eval case contract

Use `schemas/evaluation-case.schema.json`. A case declares stable ID, task, setup/fixtures, allowed and forbidden actions, expected assertions, evaluator type, thresholds, budgets, tags, and cleanup. Freeze dataset/version and prevent training-test leakage.

## Evaluators

Prefer deterministic assertions: files, schema, commands, database state, evidence count, citations, policy decisions, trace shape, latency, and budgets. Use model judges only for subjective dimensions, with explicit rubric, blinded inputs, calibration examples, disagreement handling, and periodic human review.

## Metrics

Task success and verified completion, safety violation rate, prohibited action attempts/execution, tool-selection precision, citation/evidence quality, recovery, steps, tokens, cost, latency, and human escalation rate. Segment by scenario, model, provider, tenant/profile, and release.

## Regression gate

Compare candidate to baseline with identical dataset and configuration except intended changes. Fail on any critical safety regression, threshold breach, invalid cases, missing evidence for a required capability, or unexplained cost/latency increase. Do not interpret unconfigured optional integrations as missing required evidence. Store machine-readable report and trace artifacts.

Freeze input bytes, requests, attachment/scope semantics, model digest/options,
tool schemas, policy/core versions and cache cold/warm conditions for comparisons.
Count logical optimizer calls, physical model RPCs, tool/parse/render work separately.
Unknown usage is null/unknown, not invented exact tokens or cache hits. Report small
samples as samples/median/range; do not claim stable P95 or significance. Preserving
correctness and necessary coverage is a condition of a performance improvement.

## Evidence layers and final-candidate gate

| Evidence | What it does not prove |
|---|---|
| Schema/static/unit | A host dependency or primary product actually executes it |
| Rendered component/synthetic DOM | Actual GUI/transport stream/navigation or OS isolation |
| Independent tool/CLI/provider probe | Model tool visibility, matching result return, primary-product natural language |
| Primary Runtime with controlled model | Real provider compatibility or user-clicked packaged client |
| Actual primary-product E2E | Unexercised capabilities, other providers/tenants or permanent OS permission stability |

Use the actual primary entry/runtime in a new synthetic scope; do not start a
reduced parallel Demo as product acceptance. Reference-package test counts and
preview browser checks are not product gates. After the last relevant source,
prompt, configuration or UI change, rerun affected final-candidate checks and
identify what the running process actually loaded. Keep full-suite status separate
from focused green groups; overlapping counts are not additive coverage.

Retain genuine old-failure → new-result evidence. A missing-new-module red is a
feature baseline, not proof of an old production defect. Record actual command and
child exit code (not the exit of `tail` or a following command), case IDs/durations,
fingerprints, safe artifacts and the precise PASS/FAIL/SKIP/BLOCKED/NOT_RUN/UNVERIFIED
disposition. Do not invent screenshot paths, soften assertions, delete failures or
promote user confirmation of window visibility into functional GUI acceptance.

## Proportional stopping and cleanup

Run focused tests, then the relevant regression/required gates. Broaden or repeat
only for a new change, failure, missing promised evidence or unresolved risk. After
two failed similar repairs, use a new falsifiable hypothesis/official version
evidence rather than keep tweaking timeouts or rerunning identical probes. A tool
or permission blocker stays explicit; it does not justify hidden execution or a
repeated user handoff loop. Finish once the agreed gate is met.

Close owned processes before removing exact generated synthetic accounts, fixtures
and caches; retain small logs, hashes, failed cases and source rollback evidence.
Never clean an active home, unrelated project or formal runtime resource as test
cleanup. Follow [runtime-storage-operations.md](runtime-storage-operations.md).

## Acceptance scenarios

The examples in `examples/` are canonical forward scenarios, including the local
Browser/Memory and enterprise operations-console Blueprints. At least one complete
scenario should run against every release candidate. Coding-agent acceptance must
inspect, test, plan, edit, retest, inspect diff, and summarize; dangerous-operation
acceptance must require approval and avoid execution when rejected.
