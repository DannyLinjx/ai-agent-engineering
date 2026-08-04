# Testing and evaluation

Testing proves deterministic code behavior; evaluation estimates agent quality on representative tasks. Both are required.

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

No-tool response, one tool, multiple tools, tool failure/recovery, max steps, repeat/no-progress detection, user cancellation, deadline, token/cost exhaustion, checkpoint/restart, verification failure/replan, and partial irreversible side effect.

Also cover permission, context, memory, session, multi-user, MCP, routing, and subagent cases listed in their references.

## Eval case contract

Use `schemas/evaluation-case.schema.json`. A case declares stable ID, task, setup/fixtures, allowed and forbidden actions, expected assertions, evaluator type, thresholds, budgets, tags, and cleanup. Freeze dataset/version and prevent training-test leakage.

## Evaluators

Prefer deterministic assertions: files, schema, commands, database state, evidence count, citations, policy decisions, trace shape, latency, and budgets. Use model judges only for subjective dimensions, with explicit rubric, blinded inputs, calibration examples, disagreement handling, and periodic human review.

## Metrics

Task success and verified completion, safety violation rate, prohibited action attempts/execution, tool-selection precision, citation/evidence quality, recovery, steps, tokens, cost, latency, and human escalation rate. Segment by scenario, model, provider, tenant/profile, and release.

## Regression gate

Compare candidate to baseline with identical dataset and configuration except intended changes. Fail on any critical safety regression, threshold breach, invalid cases, missing evidence for a required capability, or unexplained cost/latency increase. Do not interpret unconfigured optional integrations as missing required evidence. Store machine-readable report and trace artifacts.

## Acceptance scenarios

The five examples in `examples/` are canonical forward scenarios. At least one complete scenario should run against every release candidate. Coding-agent acceptance must inspect, test, plan, edit, retest, inspect diff, and summarize; dangerous-operation acceptance must require approval and avoid execution when rejected.
