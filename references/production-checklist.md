# Production-readiness checklist

Do not call an agent production-ready until each applicable item has evidence and an owner.

## Product and governance

- objective, users, non-goals, autonomy, and prohibited uses documented;
- measurable quality/safety SLOs and launch thresholds approved;
- data classification, retention, deletion, and legal/compliance review complete;
- human escalation and incident ownership staffed.

## Runtime and reliability

- loop governed by the project's declared budgets, deadlines, cancellation and
  no-progress detection; a configured unlimited count never removes other guards;
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

## Browser and Memory profiles

- Browser authentication, CSRF, tenant/user scoping, safe Event projection, SSE
  recovery, approval replay protection, artifact authorization, accessibility, and
  dependency-backed frontend/backend/E2E gates have evidence;
- API handlers persist commands and never execute Agent tools or resolve credentials;
- one authoritative owner per Memory record family is declared (metadata/payload
  may use separate physical stores); consent, retention, correction,
  deletion, index propagation, export, and authorization-before-ranking are verified;
- selected enterprise Memory adapters have SecretRefs, health/SLO ownership, backup
  restore, rebuild, shadow migration comparison, approved cutover, and tested rollback;
- profile manifests and deployment plan match the released configuration; generated
  or planned status alone is not production evidence.

For native or other non-browser clients, apply
[client-experience.md](client-experience.md) and the selected adapter's checks;
browser cookies/CSRF/SSE are not reasons to add an HTTP product to a native client.
Native launch/package/stdio and loaded-worker evidence are described in
[native-cli-client.md](native-cli-client.md).

## Capability lifecycle and delivered product

- actual Registry → permission/selection → model wire → execution → receipt →
  model result → client paths are verified, not only standalone tools or templates;
- installed/configured/probed/authorized/runtime-bound/verified states and capability
  self-description match the current version; config or permission changes invalidate
  stale probes;
- disabled/retired dependencies cannot be resurrected by snapshots, execution,
  probes, recovery, installers or scheduled repair; no unapproved host/provider
  fallback; see [capability-readiness.md](capability-readiness.md);
- final source/prompt/config maps to the built package, actual user entry, loaded
  executable/worker and observed behavior; cached binaries/source screenshots do
  not establish the real launcher's version;
- UI/parser/independent tool/primary Runtime/model natural-language/GUI evidence
  are separated; blocked, skipped and unverified remain explicit;
- update failure preserves a complete previous artifact and private user state;
  rollback distinguishes code/config recovery from irreversible deleted data;
- owned test processes have closed before exact synthetic/cache cleanup; unrelated
  accounts, profiles and formal resources remain intact. See
  [runtime-storage-operations.md](runtime-storage-operations.md).

## Release evidence

Record code revision, artifact digest, configuration/schema versions, model profiles, tool/skill/MCP catalog versions, test/eval reports, migration plan, security approval, known limitations, owners, rollout steps, and rollback trigger. Use `schemas/production-readiness.schema.json` for a machine-readable gate.

Local build/package verification is not permission to upload or publish. Honor the
user's project-and-destination publication scope independently of repository access
or existing credentials. Do not prolong release verification after the applicable
gates pass unless a new change, failure or unresolved risk warrants another check.
