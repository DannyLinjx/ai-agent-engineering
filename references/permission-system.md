# Permission engine and human approval

All tool calls and externally visible model actions pass through deterministic authorization. The model may explain risk but may not grant permission.

## Decision flow

Validate schema → resolve identity/scope → inspect actual parameters → detect hazardous behavior → apply hard deny → apply allow rules → enforce workspace/tenant policy → enforce user/run policy → return `ALLOW`, `DENY`, or `ASK`.

Hard deny wins. An ASK result requires an unexpired approval receipt bound to user, run, tool version, normalized arguments or safe parameter boundary, target, and risk. A changed action requires new approval.

## Policy dimensions

Tool category/risk, path and workspace, command/arguments, destination/domain, database and statement type, environment, data sensitivity, recipient, volume, reversibility, tenant scope, time, rate, and actor role.

Protect at minimum `.env`, private keys, credential stores, browser cookies, system configuration, workspace-external files, destructive database statements, force push, broad deletion, system package installation, uploads, messages/email, payments, and production changes.

## Approval prompt

Show the exact intended action, tool, target, normalized parameter summary, reason, data exposed, blast radius, reversibility, rollback, expected cost/time, and recommendation. Offer a safer alternative. Never hide multiple materially different actions under one approval.

## Path and command guards

Resolve real paths, reject traversal/symlink escape, and use explicit workspace roots. Prefer argument arrays and non-shell execution. Detect destructive flags, privilege escalation, pipe/redirection/substitution, encoded payloads, broad globs, remote execution, and environment-secret expansion. Parameterize database operations and default to read-only.

## Credentials

Use a secret manager or injected short-lived credential reference. Tools receive only required credentials at execution time. Never put secrets in prompts, memory, checkpoints, artifacts, traces, or approval text.

## Tests

Cover in-workspace and out-of-workspace access, sensitive files, normal and destructive writes, ordinary and high-risk commands, upload/communication, production scopes, expired or rejected approval, argument mutation after approval, tenant mismatch, logging redaction, and policy precedence.

Use `templates/permission-policy.yaml`, `schemas/tool-manifest.schema.json`, and `scripts/audit_agent_safety.py`.

## Publishing generalized experience

Permission to update a reusable Skill does not permit publishing its source
projects. Publish general methods and independently synthetic examples. Exclude
project names, profiles, code, internal architecture/configuration, paths,
screenshots and operational history unless the user separately authorizes those
exact disclosures to that destination. Inspect payload meaning as well as secret
patterns: a project description can be out of scope without containing a secret.
A normal cleanup commit leaves its parent history accessible; report that limit
and obtain the necessary authority before destructive history changes.

## Authorization continuity and human input

Keep an authority ledger for the actual action/target/payload/scope/expiry. A still-valid grant for the same material operation can cover necessary steps of the requested task; do not ask at every phase or every public read. Changed destinations, private-data-derived queries, shared-service changes, installation, system permissions or higher-risk effects may require a new decision. Download authority is not private-data egress or cloud-tracing authority.

Ask User clarification is not an approval receipt. Client `approved_by` or model `approved=true` cannot mint authority. Moving management into a personal Settings menu does not change backend workspace/admin rights; direct routes/IPC/CLI calls enforce the same checks. Revocation applies before cached/derived plaintext access, execution and final delivery.

Use the platform's normal approval mechanism. Do not manipulate system permission stores, bypass a lock screen, weaken isolation, change shells/languages or hide background execution after rejection. Explain the exact blocked action and continue unaffected authorized work. For explicitly authorized irreversible disposal, record the precise data-loss boundary rather than claiming a nonexistent rollback or storing an unwanted giant duplicate.
