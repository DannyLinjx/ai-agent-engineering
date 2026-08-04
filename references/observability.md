# Observability, audit, and cost

Every run needs an end-to-end correlation path from interface request through planning, model calls, permission decisions, tools, checkpoints, verification, and response.

## Signals

- **Logs:** structured events with timestamp, severity, tenant-safe IDs, component, event, status, duration, and error category.
- **Traces:** spans for context build, routing, model attempts, tool authorization/execution, persistence, subagents, MCP, and verification.
- **Metrics:** request/run success, latency, steps, tokens, estimated cost, tool/model errors, denials/approvals, loop terminations, compactions, queue depth, checkpoint/recovery, verifier/eval rates.
- **Audit:** append-only security and externally visible actions with actor, policy/config version, decision, approval receipt, target summary, side-effect receipt, and integrity protection.

Never log passwords, API keys, cookies, private message bodies, complete tool outputs, or raw sensitive prompts. Redact at source and test redaction. Use sampling only for diagnostic telemetry, not mandatory audit events.

## SLOs and alerts

Define user-facing availability and latency, successful verified completion, cancellation responsiveness, recovery success, policy error rate, cost per successful run, and tenant-isolation incidents. Alert on runaway loops/cost, approval anomalies, repeated denied actions, provider/tool outage, queue staleness, checkpoint failures, eval regressions, and redaction failure.

## Evaluation linkage

Trace events carry scenario/eval case IDs, dataset version, model/prompt/config fingerprints, and evidence paths. Production dashboards separate model quality failures from runtime, tool, policy, and dependency failures.
