# Production-readiness checklist

Do not call an agent production-ready until each applicable item has evidence and an owner.

## Product and governance

- objective, users, non-goals, autonomy, and prohibited uses documented;
- measurable quality/safety SLOs and launch thresholds approved;
- data classification, retention, deletion, and legal/compliance review complete;
- human escalation and incident ownership staffed.

## Runtime and reliability

- bounded loop, budgets, deadlines, cancellation, no-progress detection;
- idempotency, retries, checkpoints, recovery, reconciliation, and migrations tested;
- dependency timeouts, circuit breakers, degraded modes, and capacity limits defined;
- safe shutdown and backpressure verified.

## Safety and security

- threat model current; least-privilege tools and credentials;
- deterministic permission policy, approvals, workspace/tenant isolation;
- prompt-injection and untrusted-content controls;
- secret redaction, supply-chain scanning, dependency pinning, and vulnerability response;
- destructive and externally visible actions tested end to end.

## Quality

- contract/unit/integration/E2E/security/recovery/isolation suites pass;
- versioned eval set and baseline comparison pass;
- verifier covers completion criteria and negative cases;
- trace review finds no hidden retries, policy bypass, or evidence gaps.

## Optional integration declaration

- at least one real Model Provider is enabled and verified for a live production agent;
- Channel adapters are required only if the product charter promises those entry points;
- MCP servers are required only if an acceptance criterion depends on them;
- disabled/unselected adapters are reported `not_applicable`, not failed or silently tested;
- every selected adapter uses credential references, health checks, timeouts, isolation, and adapter-specific tests.

## Operations

- dashboards, alerts, SLOs, audit retention, cost budgets, and quota alerts;
- on-call runbook, incident severity, kill switch, rollback, and provider outage plan;
- canary/feature flags, staged migration, backup restore, and disaster recovery tested;
- configuration provenance and model/prompt/tool/skill version rollback available.

## Release evidence

Record code revision, artifact digest, configuration/schema versions, model profiles, tool/skill/MCP catalog versions, test/eval reports, migration plan, security approval, known limitations, owners, rollout steps, and rollback trigger. Use `schemas/production-readiness.schema.json` for a machine-readable gate.
