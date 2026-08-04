# Session, checkpoint, artifact, and persistence

A session represents a conversation or task history. A run is one execution attempt. A checkpoint is a durable recovery boundary. An artifact is an immutable or versioned externalized result.

## Minimum entities

Users, agents, sessions, messages, runs, checkpoints, tool runs, approvals, artifacts, memories, model calls, configuration versions, audit logs, and eval runs. Every record carries tenant/user scope and stable IDs.

## Persistence rules

- use transactions for state transition plus audit/event append;
- use optimistic concurrency or leases to prevent two workers resuming the same run;
- version serialized state and provide migrations;
- store hashes and content types for artifacts;
- separate secret references from configuration;
- make retention and deletion explicit;
- reconcile `running` tool/model calls after crash.

## Checkpoint content

Persist plan and current step, messages or summary, observation/artifact references, tool receipts, approvals, budget usage, status, structured errors, effective configuration hash, model/tool/skill versions, and event cursor. Create checkpoints after meaningful progress and before approved high-risk actions.

## Resume and rewind

Resume validates checkpoint integrity, schema/config compatibility, authorization, artifact availability, and in-flight side effects. Rewind creates a new branch or event rather than destroying audit history. It must state which external side effects cannot be undone.

## User operations

Provide new, list, resume, history, rewind, and cancel operations. Cancellation is durable and propagates to active work. Session export must redact secrets and respect tenant boundaries.

## Recovery tests

Test process crash before and after tool commit, duplicate delivery, stale lease takeover, incompatible checkpoint, missing artifact, cancelled resume, rewind with irreversible side effect, and multi-user isolation.
