# Multi-agent workflow: research, implement, test, review

## Parent objective

Deliver a verified feature while keeping authority, budgets, and final completion with the parent agent.

## DAG

1. Research agent: read-only discovery, architecture constraints, evidence artifact.
2. Coding agent: depends on research; workspace read/write and focused commands; implementation artifact.
3. Testing agent: depends on code; read and test execution; test report.
4. Review agent: depends on code and tests; read-only security/correctness review.
5. Parent verifier: resolves contradictions, runs critical checks, and maps evidence to completion criteria.

## Task contract example

Each task receives objective/non-goals, artifact inputs, expected result schema, max steps/tokens/cost/time, allowlisted tools/skills, tenant/workspace scope, and escalation conditions. No subagent can push, deploy, send messages, access credentials, or recursively delegate unless explicitly authorized.

## Merge rules

Use stable finding IDs and evidence paths. Conflicting findings remain explicit and trigger parent resolution. A partial/failed dependency blocks dependent mutation. Parent context receives summaries and artifact references, not transcripts.

## Acceptance

Trace correlation connects all child runs; aggregate budget stays below the parent cap; cancellation reaches all children; permissions and tenant scope remain independent; final verifier—not majority vote—decides completion.
