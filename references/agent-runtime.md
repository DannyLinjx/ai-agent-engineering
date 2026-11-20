# Agent runtime, planner, and loop

## Runtime responsibilities

The runtime receives a normalized task, initializes state and budgets, builds context, calls the model, parses typed decisions, authorizes and dispatches tools, records observations, checkpoints progress, replans when evidence changes, invokes verification, and returns a result envelope.

It must not contain provider-specific HTTP code, filesystem logic, permission rules, long-term memory policy, or UI formatting.

## Loop invariants

Before every iteration check cancellation, deadline, configured count caps, model/tool/token/cost budgets, consecutive failures, repeated action fingerprint, and progress. After every tool result validate the envelope, offload oversized output, update state, emit telemetry, and persist a checkpoint. Identify the existing loop and owners first; do not add an inner Agent over the same tools merely to introduce dynamic prompts, optimization, routing or a framework helper.

Required limits:

- total and per-model-call timeout;
- total and per-tool timeout;
- explicit step/replan/retrieval-count policies, with documented disabled-cap semantics;
- input/output/total tokens and estimated cost;
- maximum consecutive failures;
- maximum identical or semantically equivalent actions;
- maximum artifacts and retained observation bytes.

An action fingerprint should include normalized tool name and canonicalized arguments. A progress fingerprint may combine plan state, changed artifacts, new evidence IDs, and verifier deltas. Repeated actions without progress terminate as `no_progress`, not as a successful answer.

Some projects explicitly define `0` as no fixed cap for a particular count. That
does not disable deadlines, cancellation, context limits, resource policy or
no-progress detection. Distinguish graph steps, retrieval pages and required
business-check coverage; a small arbitrary count must not silently omit necessary
checks or turn incomplete work into `pass`. Generated runtimes must either implement
the declared zero semantics or reject that configuration honestly.

## Planner trigger

Use a structured plan when the task touches multiple files/systems, has dependencies, produces several artifacts, changes code/data, calls multiple tools, contains risk, requires delegation, or has multi-stage acceptance. A trivial read or answer may skip a full plan but still needs budgets and a completion criterion.

Each step declares objective, dependencies, required capabilities, expected side effects, verification method, status, and evidence. Replanning preserves completed evidence and explains what changed.

Use the user's existing phase plan/contracts when provided rather than replacing
them with generic phases. For documents and deterministic workflows, the program
advances bounded batches/cursors and reuses committed receipts; do not ask the
model to plan each page again. See `document-source-pipelines.md`.

## Model decision envelope

Do not parse free-form prose for control flow. Require a typed decision with one of:

- `respond`: candidate response plus claimed criteria;
- `tool_call`: tool name, arguments, reason, expected evidence;
- `replan`: reason and plan delta;
- `request_approval`: intended action and risk;
- `delegate`: bounded task contract;
- `fail`: structured reason and recoverability.

Reject unknown tools, invalid schemas, over-budget calls, or decisions inconsistent with state.

## Retry and recovery

Use a single existing, capped retry policy only for declared transient failures.
Do not automatically add backoff, summary, fallback or optimizer retry layers.
Never retry a non-idempotent side effect unless the executor has an idempotency key
and reconciles whether the first attempt committed. An unknown outcome stays
unknown until checked. After a recoverable error, append evidence and replan only
when evidence/state changes; do not repeat the same model prompt unchanged.

On restart, load the latest valid checkpoint, verify configuration compatibility, reconcile in-flight tool runs, rehydrate artifact references, and resume from an explicit state transition. A checkpoint should include version, state, plan, effective configuration hash, budgets, tool receipts, artifacts, errors, and audit cursor.

## Completion

The runtime may enter `completed` only after the verifier maps evidence to every required completion criterion. If verification fails, replan within budget or return `failed`/`partial` with unmet criteria. A fluent model message is not evidence.

## Cancellation

Propagate cancellation to streaming model calls, tools, subprocess groups, network
requests, subagents and durable jobs. Request acceptance is not terminal confirmation:
persist `cancelled` only at the verified boundary, otherwise retain an unconfirmed
cleanup/remote-effect state. Epoch/version fences prevent late commits; report
committed versus uncommitted side effects. Pause admits no new work but may allow
one safe already-admitted batch to commit, then resumes the same Run/cursor and
spent budgets. Closing a view or disconnecting transport is not cancellation.
