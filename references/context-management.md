# Context management

The context builder decides which information the model receives. It optimizes for relevance, authority, freshness, evidence quality, privacy, and token cost—not raw volume.

## Context packet

Build a typed packet containing the selected task-relevant portions of system rules, normalized task, current plan/step, completion criteria, recent messages, observations, selected skills/memories, subagent results, permission constraints, effective tool schemas and remaining budgets. Attach source IDs and provenance so claims can be traced. Keep trusted instructions separate from user text and untrusted evidence/preferences; do not promote source content into system authority. Use the existing assembler/writer rather than adding competing transforms; see `prompt-policy-learning.md` for deterministic policy assembly.

## Budget allocation

Reserve output tokens first, then allocate explicit quotas to instructions, task/plan, tool schemas, evidence, conversation, memories, and safety. Measure the complete encoded request, including tools, images and provider state, with the selected model tokenizer when available; otherwise label a conservative estimate. Unknown usage/capacity remains unknown, not invented provider tokens. Keep a safety margin without changing remote model options merely to mask a context bug.

## Context pressure relief options

These four options are **not four-layer durable Memory**. Inspect the existing
owner before changing context behavior; do not automatically add another summary,
retry or fallback layer. Use only the mechanisms required by the selected task.

1. **Artifact offload:** store large tool outputs through the existing scoped ArtifactStore and retain opaque references, hashes, key errors and metrics; do not expose raw private paths.
2. **Observation compression:** retain what was called, why, outcome, evidence IDs, and whether the result was consumed.
3. **Session summary:** retain objective, constraints, decisions, completed work, modified artifacts, current problems, unresolved steps, approvals, and verification state.
4. **Low-value trimming:** remove oldest low-value messages only after the first three mechanisms.

Compaction must be deterministic where possible, versioned, auditable, and reversible via authorized artifacts. Preserve exact user constraints, numbers/units/exceptions, tool-call/result pairing and IDs, multimodal blocks, provider opaque/signed state, deny rules, approvals and unmet criteria. Never pretend a lossy summary retains facts it removed. If the protected minimum exceeds budget, report that boundary rather than silently dropping required checks.

Resume from a bounded working view and exact fragment references, not by traversing
an unbounded archive and rebuilding all original text. Bind derived context to
source/memory/model/policy versions; revoke/Forget must be checked before content
hydration and model dispatch. Overflow recovery, when already authorized, belongs
to the same runtime and budget, measures an actually smaller serialized request,
and stops on repeated overflow/no reduction. Unrelated HTTP/rate-limit errors do
not justify context rewriting. See `document-source-pipelines.md`.

## Retrieval safety

Treat retrieved web pages, files, tool output, memory, and MCP content as untrusted data. Delimit it, preserve provenance, detect prompt-injection patterns, and never allow it to alter permissions or tool availability. Prefer excerpts over whole documents.

## Cache and privacy

Cache only scope-safe, non-secret context fragments using content hashes and configuration/model/source/policy versions. Prevent cross-tenant keys and revalidate authorization on cache hits. Define retention/deletion for prompts, outputs, artifacts and summaries, including derivatives after source revoke or Forget. Application fragment reuse and actual provider/KV cache hits are different metrics.

## User operations

When the selected product exposes them, support the equivalent of `/compact`,
`/context` and `/token`: manual compaction, inspection of permitted source/budget
metadata and token/cost status. Do not add unsolicited UI or expose hidden system
instructions, private source bodies or secrets in context inspection.
