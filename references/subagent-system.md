# Subagent system

Delegate only independent, bounded work that benefits from separate context or parallel execution. Stabilize the single-agent loop before adding delegation.

## Task contract

Each task declares ID, objective, non-goals, input artifact references, expected output schema, completion criteria, deadline, token/cost/step budgets, tool/skill/MCP allowlists, tenant/workspace scope, data sensitivity, and escalation behavior.

Each subagent has independent context, state, logs, cancellation, checkpoint, and budgets. It cannot inherit broad credentials or tools by default and cannot delegate again unless explicitly permitted.

## Result contract

Return `success`, `partial`, or `failed`; summary; findings; evidence; artifact references; unmet criteria; unresolved issues; consumed budgets; and recommended next actions. The parent consumes the structured result, not the entire transcript.

## Scheduling and merge

Build a dependency DAG. Limit fan-out, concurrency, and total budget. Cancel downstream work when prerequisites fail. Merge results by stable keys and evidence provenance; flag contradictions instead of letting the last writer win. Only the parent verifier may decide overall completion.

## Safety

Apply the same permission and audit pipeline to subagent tool calls. Prevent cross-tenant context, secret inheritance, artifact path escape, and unbounded recursive delegation. Approval belongs to the actual side effect and actor/run.

## Tests

Cover successful fan-out, dependency failure, partial result, contradictory findings, deadline/cancel, tool isolation, budget exhaustion, artifact merge, tenant isolation, and trace correlation.
