# Model provider and routing

Hide provider SDKs behind a common gateway supporting messages, structured output, tool calling, streaming, usage, cancellation, errors, and health.

Use a deterministic mock gateway for development, unit tests, runtime scenarios, and offline evals. A user may select `mock`, `none`, `auto`, or `configured` in `integrations.config.json`. No live provider is required until a live inference criterion or production profile requires it. An unselected live-provider test is skipped in development/test, not treated as a core failure.

## Model profile

Record provider/model ID, modalities, context/output limits, tool/JSON support, reasoning tier, data residency/privacy, availability, latency SLO, token prices, rate limits, and fallback group. Version profiles and record the selected profile per run.

## Routing inputs

Task type and difficulty, modality, privacy class, context size, tool/JSON requirements, latency target, quality threshold, budget, provider health, tenant policy, and regional constraints. Deterministic hard constraints filter candidates before a scoring rule selects among them.

Typical mapping: fast low-cost for simple Q&A, reasoning for complex planning, coding for implementation/review, vision for images, long-context for large synthesis, local/private for restricted data. Do not use unsupported model capabilities based on model-generated claims.

## Fallback

Use only an explicitly selected fallback policy, for example preferred compatible
model → authorized compatible secondary → explicit failure. Existing projects may
forbid fallback; adding a routing component does not authorize a second model,
cloud service, retry loop or private-data destination. Every selected fallback must
still meet privacy, modality, tool, schema, context and quality constraints.

When selection is `none`, expose a clear `provider_not_configured` result only if live inference is actually invoked. Continue all provider-independent engineering and verification work. When selection is `mock`, never present mock results as live-provider or production evidence.

## Query engine

Validate request size and schemas, attach idempotency/correlation IDs, stream with cancellation, apply per-attempt and total deadlines, retry only explicitly retryable transient errors through the existing retry owner, enforce usage/cost caps, validate structured output, and emit redacted telemetry. Preserve message blocks, tool-call/result IDs and provider-specific opaque/cache metadata. Test tool calling, JSON-schema structured output, images and streaming independently. A saved profile or one successful protocol probe is not proof of every capability; direct HTTP reachability also does not prove a packaged App has OS network permission.

## Advisory intent/next-step routing

An optional fast classifier may advise the existing runtime without becoming a
parallel planner or answer/tool loop. The host first derives legal typed candidates
from explicit mode, pinned workflow, pending calls/interrupts and public progress.
Give the advisor only minimal permitted question/clarification and progress data;
no full documents, memory files or hidden reasoning. The advisor selects opaque
candidate IDs and cannot add tools, parameters, permissions, sources or budgets.

Classify each accepted new input as required, persist/version the advisory result
for replay, and avoid repeated classification on duplicate/resumed steps. Explicit
user mode and pending deterministic work win. Cold/busy, abstain, low-confidence,
invalid, timed-out, cancelled or late advice stays on the main path under declared
policy. The primary model/Tool Gateway still validates parameters and completion.
Choose the classifier implementation only from the current product's approved
dependencies. Installation/inference success is separate from calibrated semantic
quality.

## Tests

Test each hard constraint, budget boundary, provider outage, rate limit, malformed structured output, stream cancellation, fallback compatibility, privacy restriction, context overflow, and usage accounting.
