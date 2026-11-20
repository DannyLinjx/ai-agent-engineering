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

## Measurement provenance and final identity

Separate logical optimizer/model operations, physical provider RPCs, tool calls, parse/render executions and UI events. Meter failed attempts too. Provider-reported tokens, local estimates, raw wire bytes and unknown usage are distinct; absent values remain unknown/null. Record model/config/tool/policy/source versions and cache cold/warm conditions without raw private payloads.

A local model does not imply local tracing: inspect inherited callbacks/exporters and actual destinations, and disable unapproved cloud telemetry. Do not expose system prompts, hidden reasoning, internal paths or secrets in client state, screenshots or public traces.

Link source → build/package digest → actual launcher → loaded worker/interpreter/config → observed behavior. Saving a file or building a cached binary does not prove the running product loaded it. Keep component/tool/Runtime/natural-language/GUI/isolation evidence separate; compact local records must include real exit codes, failed/skipped/unverified cases, actual artifact hashes and scope/coverage.

Small samples support single-run, median and range comparisons; do not publish stable P95 or statistical-significance claims from a few runs. Compare correctness and necessary coverage alongside speed, not fewer checks or falsely completed tasks.
