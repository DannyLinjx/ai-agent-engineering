# Deterministic prompts and controlled policy learning

Read this when adding dynamic prompts, reusable feedback, prompt optimization, or
policy publication to an existing Agent. It describes one extension of the selected
runtime, not another planner, memory store, model/tool loop, or mandatory dependency.
Use `memory-system.md` for consent and memory lifecycle and `model-routing.md` for
the existing gateway. Framework-specific examples below are conditional on selection.

## 1. Locate the single normal-call boundary

Map every system/developer writer, canonical message builder, context/compaction
owner, model node, gateway, checkpoint, feedback endpoint, job/outbox and settings
owner. Trace an actual request; a class or sample directory does not prove wiring.
Preserve the user's framework and authorized phase plan. If a complete work unit
already uses an official dynamic-prompt API, use it there; do not wrap a second
`create_agent` around an outer loop that already owns the same tools.

Add a pure assembler at the existing model admission point:

```text
immutable core + output contract + pinned permitted policy
→ deterministic trusted prompt
canonical user/task + scoped untrusted evidence/preferences + tool messages
→ existing model gateway
```

- Preserve the existing fixed core and output protocol. Mutable policy must not
  change permissions, evidence requirements, business facts or tool availability.
- Keep task/user text, retrieved pages, uploads and feedback at their original
  lower-trust message boundary. A dynamic prompt is not permission escalation.
- Migrate the identified writer explicitly; do not silently delete existing
  system/developer messages or append another copy on each turn.
- Equal effective configuration produces byte-stable trusted prefixes. Keep run
  IDs, timestamps and log metadata outside natural-language system content.
- Preserve multimodal blocks, tool schemas, call/result IDs, provider opaque and
  signed blocks, cache metadata, stream mode, remaining deadline and cancellation.
- Normal assembly makes **zero additional model requests**. Record effective
  prompt hash, core/policy versions and compatibility fingerprints locally; do not
  expose raw system prompts or hidden reasoning in public diagnostics.
- Pin policy ref/hash/scope/generation and compatibility at Run start. Resume uses
  that pin and checks revocation before each actual call, not merely at UI load.
- A feature switch can retain the prior prompt path without recreating sessions
  or discarding client drafts. Do not add new summary/retry/fallback layers as a
  side effect of this change.

## 2. Separate correction, memory and learning

| User intent | Effect |
|---|---|
| This task only | Apply the correction/scope change to the current task under existing rules; no optimizer. |
| Future similar tasks, with consent | Persist a reusable-feedback candidate in the authorized personal/project scope. |
| Implicit dissatisfaction or unscoped negative feedback | Signal for review; not authority to publish personal or workspace rules. |

The backend derives actor, scope, source Run, source policy and idempotency key.
Do not trust frontend `approved_by` or model `approved=true`. A personal approval
does not grant workspace policy rights. Distinguish ordinary memory records from
executable policy candidates and from canonical Run state.

Reuse the existing feedback service and durable outbox/job mechanism. Persist a
minimal approved synthetic/redacted episode: the relevant correction, necessary
observations, intended reusable constraint and source/version references. Do not
collect whole conversations, complete files, secrets or hidden chain-of-thought.

Jobs need a scoped idempotency identity including feedback and base generation,
restart recovery, cancellation, authorization revalidation and late-result fencing.
Normal conversation must not wait for learning. When sharing a model server,
schedule learning behind foreground work; background execution still competes
for GPU/CPU/queue capacity.

## 3. Use the real optimizer through the existing gateway

Select and pin an optimizer only when the requested learning workflow needs it.
Do not auto-install LangMem or switch to a sample cloud model. Adapt SDK model
interfaces thinly around the existing authorized model factory/gateway; keep
protocol selection, secret resolution, minimization, logging, timeout, cancellation
and metering in that path.

For a **selected LangMem implementation**, inspect the installed API/source and
run synthetic compatibility probes before reporting support:

```python
# Illustrative pinned-version contract, not a package-install instruction.
model.with_structured_output(OutputSchema, method="json_schema")
optimizer = create_prompt_optimizer(model, kind="prompt_memory")
```

Use a compatible model object, not an unsupported gateway string. Explicitly
select `kind`; verify prompt-memory configuration for that version rather than
copying gradient/reflection options. Function calling alone does not prove
JSON-schema structured-output compatibility. Verify placeholder/healer behavior
before passing templates; never globally replace braces to hide a parsing error.

Pass only mutable policy, update instructions and the minimum permitted trajectory.
Restrict the candidate language for the initial release to reviewed schema/slots;
if an SDK operates on text, use a strict reversible boundary representation and
validate back into the internal schema. The project's number/names of slots are
configuration, not universal Skill requirements.

| Optimizer outcome | Durable disposition | Active policy |
|---|---|---|
| Empty or unchanged validated policy | `NO_CHANGE` | unchanged |
| Invalid structure, unknown fields, excessive length or forbidden mutation | `REJECTED` / `QUARANTINED` | unchanged |
| Protocol failure, timeout or cancellation | failed/cancelled with actual error | unchanged |
| Valid candidate | pending evaluation/review | unchanged |

Disable unapproved cloud tracing and inspect inherited callbacks, exporters and
actual egress. A local inference model does not imply local telemetry. Count one
logical optimizer invocation separately from all physical model requests. Reuse
one bounded retry owner, if authorized; do not stack optimizer, adapter and outer
runtime retry loops. Incompatibility is `blocked`, not permission to silently use
another model or to discard working prompt/feedback functionality.

## 4. Evaluate, review and publish

Use the existing persistent repository for policy versions, candidates, jobs and
audit. An in-memory reference repository is not a production implementation.
Evaluation evidence binds:

```text
candidate digest + evaluation suite hash + immutable core/output contract
+ model/profile/digest/parameters + tool/schema/permission fingerprints
+ relevant source and evaluator versions
```

Evaluate normal tasks and negative cases for evidence, scope, injection, missing
information, failed tools and cancellation. Semantic safety cannot rely solely on
keyword regexes or the optimizer's self-score. Keep generation, evaluation,
human review and publication as separate states. For an initial learning release,
require an authorized human to review the candidate/diff and bound evaluation;
workspace publication additionally requires the appropriate administrator role.

Publish with compare-and-swap on the expected active generation. Revalidate
authorization, candidate digest, evaluation identity and cancellation at commit.
If the base generation or compatibility changes, mark the candidate stale and
rebase/re-evaluate; do not publish a previously green candidate blindly. Duplicate
feedback/job delivery must not publish twice.

Existing Runs retain their pinned policy. Rollback creates a new audited generation
with earlier content; it is not deletion/reuse of history. Emergency revocation is
separate and prevents the next model call or resume from using a revoked pin.
Late optimizer/evaluator responses cannot publish after cancel or revocation.

## 5. Client state and verification

Put management in the product's existing settings/memory area, not an unsolicited
home dashboard. Show authorized scope, enablement, active version, candidate diff,
evaluation/review/publication state and permitted rollback/revoke actions. Personal
users cannot see other users' feedback or edit workspace policy. Main conversation
needs only feedback and necessary notices; safe Inspector data may include version
and local aggregate metrics, never hidden reasoning.

Use these assertions when this feature is selected:

- deterministic assembly adds no normal-path RPC, duplicates no trusted messages,
  mutates no canonical messages and retains images/tool pairs/provider state;
- wrong scope/version/stage, budget overflow and revoked pins fail before dispatch;
- one-off corrections never enqueue learning; feedback jobs survive restart and
  duplicate delivery; cancelled/revoked jobs cannot late-publish;
- real structured-output and optimizer probes exercise the selected adapter;
  malformed/no-op/timeout/cancel outcomes preserve active policy;
- failed evaluation, stale compatibility, concurrent CAS publication and rollback
  are independently checked; review is not inferred from a client-provided flag;
- the actual main Runtime and selected client/CLI read the same durable policy.

For A/B/C comparisons, freeze source bytes, questions, task scope, attachment
semantics, model/digest/parameters, tool schemas, source/config versions and cache
cold/warm conditions. Compare baseline, assembler+baseline policy and published
candidate without losing necessary checks. Record correctness/coverage, logical
and physical RPCs, repeated tools, actual/estimated tokens separately, cache,
prefill/decode, first response and total time. Small samples support per-run,
median and range reporting, not stable P95 or statistical-significance claims.
