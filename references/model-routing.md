# Model provider and routing

Hide provider SDKs behind a common gateway supporting messages, structured output, tool calling, streaming, usage, cancellation, errors, and health.

Use a deterministic mock gateway for development, unit tests, runtime scenarios, and offline evals. A user may select `mock`, `none`, `auto`, or `configured` in `integrations.config.json`. No live provider is required until a live inference criterion or production profile requires it. An unselected live-provider test is skipped in development/test, not treated as a core failure.

## Model profile

Record provider/model ID, modalities, context/output limits, tool/JSON support, reasoning tier, data residency/privacy, availability, latency SLO, token prices, rate limits, and fallback group. Version profiles and record the selected profile per run.

## Routing inputs

Task type and difficulty, modality, privacy class, context size, tool/JSON requirements, latency target, quality threshold, budget, provider health, tenant policy, and regional constraints. Deterministic hard constraints filter candidates before a scoring rule selects among them.

Typical mapping: fast low-cost for simple Q&A, reasoning for complex planning, coding for implementation/review, vision for images, long-context for large synthesis, local/private for restricted data. Do not use unsupported model capabilities based on model-generated claims.

## Fallback

Preferred compatible model → compatible secondary → authorized local model → explicit failure. A fallback must still meet privacy, modality, tool, schema, and context constraints. Do not silently downgrade below a declared quality/safety threshold.

When selection is `none`, expose a clear `provider_not_configured` result only if live inference is actually invoked. Continue all provider-independent engineering and verification work. When selection is `mock`, never present mock results as live-provider or production evidence.

## Query engine

Validate request size and schemas, attach idempotency/correlation IDs, stream with cancellation, apply per-attempt and total deadlines, retry only transient errors, enforce usage/cost caps, validate structured output, and emit redacted telemetry.

## Tests

Test each hard constraint, budget boundary, provider outage, rate limit, malformed structured output, stream cancellation, fallback compatibility, privacy restriction, context overflow, and usage accounting.
