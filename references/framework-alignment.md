# Framework alignment: Codex/OpenClaw-class engineering

“Codex-like” or “OpenClaw-like” describes product capabilities, not a license to copy proprietary internals. Align through contracts and observable behavior.

## Capability mapping

| Product behavior | Required subsystem |
|---|---|
| inspect and modify a workspace | scoped file/search/patch tools plus permission engine |
| run commands and tests | bounded executor, cancellation, output artifacts, verifier |
| multi-step autonomous work | planner, bounded runtime loop, state machine, checkpoints |
| resume and recover | durable sessions, event/audit trail, idempotent reconciliation |
| follow reusable methods | lazy skill catalog and controlled script execution |
| connect chat channels | optional Telegram, Feishu/Lark, WeCom, Slack, Teams, email, web/API adapters |
| connect apps and browsers | optional MCP/tool adapters, credentials, egress policy, approvals |
| remember durable preferences | consented scoped memory with lifecycle controls |
| use specialist workers | bounded subagent contracts and evidence merge |
| choose models automatically | capability/privacy/budget-aware router and fallback |
| operate for multiple users | immutable principal propagation and tenant isolation |
| claim work is complete | deterministic verifier plus scenario evals |
| operate in production | observability, SLOs, runbook, canary, rollback, cost controls |

## Compatibility principles

Expose provider-neutral contracts, treat channels as adapters, convert MCP tools into the same tool contract, keep skills portable markdown/resources, record configuration fingerprints, and make stored state/schema versioned. Do not bind core orchestration to one model SDK, UI, database, queue, or vendor tool format.

## Maturity levels

1. **Assistant:** one model call, no side effects.
2. **Tool agent:** bounded tool call with validation and permission.
3. **Durable agent:** plan, loop, session, checkpoint, context, verifier.
4. **Extensible agent:** skills, hooks, memory, MCP, routing, subagents.
5. **Production platform:** tenant isolation, evals, audit, SLOs, deployment/rollback, incident response.

Do not market a level before its exit evidence exists.
