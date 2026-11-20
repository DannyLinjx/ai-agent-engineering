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

Persist plan/current step, bounded message/context references, tool receipts,
approvals, budget usage, status, errors, effective configuration hash,
model/tool/skill/policy versions and event cursor. Keep canonical payload storage
separate where the project's privacy model requires it; a checkpoint need not
duplicate full messages or reconstruct a whole document. Do not add a new summary
system merely because the checkpoint can reference one. Create checkpoints after
meaningful progress and before approved high-risk actions.

## Resume and rewind

Resume validates checkpoint integrity, schema/config/policy compatibility,
authorization, current source generations/snapshots, artifact availability and
in-flight side effects. Validate revoked sources/memory before decrypting or
delivering derived answers, summaries and old context, not only at a UI/API route.
Committed receipts/cursors are reused without repeating successful effects.
Rewind creates a branch/event rather than destroying audit history and states which
external side effects cannot be undone. Reinstallation cannot revive a retired
capability without current authorization; see [capability-readiness.md](capability-readiness.md).

## User operations

Provide new, list, resume, history, rewind, and cancel operations. Cancellation is durable and propagates to active work. Session export must redact secrets and respect tenant boundaries.

## Control, event and user-input semantics

Distinguish a control request, its accepted acknowledgement and confirmed Runtime
state. A client must not treat HTTP202 or a stdio ACK as Paused/Cancelled. Show
pending states while the owned model/tool/worker drains to a safe boundary. Pause
blocks new admission while an already admitted complete batch may be committed;
resume continues the same run, pinned versions, cursor and cumulative budgets.
Cancellation targets actual owned work, not merely a subscription/connection.
When remote termination cannot be confirmed, keep that fact unconfirmed.

Persist event sequence, expected epoch/version and idempotency for controls and
input. Fence late work after cancel/revoke and deduplicate replayed final events.
Reconnect restores authoritative snapshot/cursor before new events. Starting a new
conversation or closing settings does not implicitly cancel the previous run.

Ask User is a typed durable interrupt, separate from permission approval. Bind
question/options/custom-input policy to interrupt and run IDs; submit with a stable
input ID and expected epoch. Duplicate clicks reuse that ID, changed content with
the same ID conflicts, and cancelled/revoked runs reject input. Resume the original
thread/run from the accepted input rather than resending the prior model call.

For CLI clients, keep machine-readable events/results on stdout and diagnostics on
stderr. Document whether an interrupt requests cancellation, detaches, or leaves a
durable waiting-input run; do not conflate those outcomes. See
[client-experience.md](client-experience.md) for projection and draft/identity rules.

## Recovery tests

Test process crash before/after tool commit, duplicate delivery/final/input, stale
lease/epoch, pause boundary and same-run resume, revoked source before plaintext,
incompatible policy/checkpoint, missing artifact, cancelled resume, remote-stop
uncertainty, rewind with irreversible effect and multi-user isolation. Synthetic
worker cleanup does not prove arbitrary external-service termination.
