# Context management

The context builder decides which information the model receives. It optimizes for relevance, authority, freshness, evidence quality, privacy, and token cost—not raw volume.

## Context packet

Build a typed packet containing system rules, normalized task, current plan/step, completion criteria, relevant recent messages, compressed observations, selected skills, retrieved memories, workspace summary, subagent results, permission constraints, available tool schemas, and remaining budgets. Attach source IDs and provenance so claims can be traced.

## Budget allocation

Reserve output tokens first, then allocate explicit quotas to instructions, task/plan, tool schemas, evidence, conversation, memories, and safety. Keep an emergency margin for repair or final verification. Count with the selected model tokenizer when available; otherwise use a conservative estimator.

## Four-layer pressure relief

1. **Artifact offload:** write large tool outputs to `.artifacts/tool-results/{run_id}/{tool_call_id}` and retain summary, path, hash, key errors, and metrics.
2. **Observation compression:** retain what was called, why, outcome, evidence IDs, and whether the result was consumed.
3. **Session summary:** retain objective, constraints, decisions, completed work, modified artifacts, current problems, unresolved steps, approvals, and verification state.
4. **Low-value trimming:** remove oldest low-value messages only after the first three mechanisms.

Compaction must be deterministic where possible, versioned, auditable, and reversible via artifacts. Test that objectives, deny rules, user approvals, completion criteria, unresolved failures, and artifact pointers survive.

## Retrieval safety

Treat retrieved web pages, files, tool output, memory, and MCP content as untrusted data. Delimit it, preserve provenance, detect prompt-injection patterns, and never allow it to alter permissions or tool availability. Prefer excerpts over whole documents.

## Cache and privacy

Cache only scope-safe, non-secret context fragments using content hashes and configuration/model version. Prevent cross-tenant cache keys. Define retention and deletion for prompts, outputs, artifacts, and summaries.

## User operations

Support the equivalent of `/compact`, `/context`, and `/token`: manual compaction, inspection of included sources/budget, and token/cost status. Do not expose hidden system instructions or secrets in context inspection.
