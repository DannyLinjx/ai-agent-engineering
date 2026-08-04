# Agent acceptance test plan

## Release under test

- Revision/config/model/tool/skill/MCP versions:
- Environment and dataset version:
- Baseline:

## Gates

| Gate | Command/case IDs | Threshold | Evidence | Result |
|---|---|---:|---|---|
| Static and unit | | 100% pass | | |
| Integration | | 100% critical pass | | |
| Agent loop | | no prohibited actions | | |
| Security/permissions | | 0 critical violations | | |
| Recovery/isolation | | 100% critical pass | | |
| Offline eval | | | | |
| Cost/latency | | no unexplained regression | | |

## Optional integration matrix

| Integration | Selection | Required? | Test status | Evidence/skip reason |
|---|---|---:|---|---|
| Live Model Provider | mock/none/auto/configured | | | |
| Channel adapters | none/configured | | | |
| MCP servers | none/configured | | | |

Unconfigured optional integrations are `skipped` or `not_applicable`; required integrations may not be skipped.

## Mandatory scenarios

No tool, one tool, multi-tool, tool failure, repeat detection, cancel, timeout/budget, checkpoint recovery, permission deny/ask/reject, compaction, memory conflict, tenant isolation, model fallback, MCP failure, subagent partial result, verification failure/replan, and dangerous-operation refusal.

## Decision

- Go/no-go/conditional:
- Known limitations/residual risk:
- Owners and expiry for exceptions:
