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
