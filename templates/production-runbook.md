# Production runbook: {{AGENT_NAME}}

## Service map and ownership

- Components/dependencies:
- On-call and escalation:
- Dashboards/logs/traces:

## SLOs and alerts

| Signal | Target | Alert | Triage query |
|---|---:|---:|---|

## Common incidents

### Runaway loop or cost

Detection, kill switch, affected-run query, user impact, recovery, and regression case.

### Model/provider outage

Fallback compatibility, circuit breaker, degraded mode, and recovery verification.

### Tool/MCP failure

Disable path, queued work, side-effect reconciliation, and dependency owner.

### Suspected data or tenant leak

Containment, credential revocation, evidence preservation, notification owner, and deletion/correction.

## Deploy and rollback

- Preconditions and migration backup:
- Canary steps and metrics:
- Rollback triggers:
- Rollback commands/procedure:
- Post-rollback verification:
