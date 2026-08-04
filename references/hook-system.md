# Hook system

Hooks inject deterministic lifecycle behavior without modifying the runtime core.

## Events

Support Pre/PostSessionStart, Pre/PostContextBuild, Pre/PostModelCall, Pre/PostToolUse, OnToolError, Pre/PostCompact, Pre/PostFinalAnswer, and OnSessionEnd. Add versioned payload schemas and correlation IDs.

## Semantics

Define ordering, priority, sync/async behavior, timeout, retries, idempotency, mutability, failure mode, and audit behavior per hook. Pre-hooks may reject or narrowly transform a typed request; post-hooks may annotate results but cannot retroactively authorize a denied side effect.

Critical security hooks fail closed. Telemetry/formatting hooks may fail open with alerts. Avoid unbounded hook recursion and prevent hooks from invoking arbitrary tools outside the same permission path.

## Typical hooks

Sensitive-path guard, command inspection, prompt-injection scan, format-after-edit, focused test after code change, error artifact capture, memory candidate extraction, artifact registration, output schema check, diff generation, and session report.

## Tests

Test ordering, timeout, failure policy, duplicate delivery, mutation boundaries, nested events, cancellation, sensitive-data redaction, and the guarantee that a hook cannot bypass permissions.
