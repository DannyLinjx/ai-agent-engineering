# Troubleshooting playbook

## Infinite or repetitive tool loop

Inspect normalized action fingerprints, progress signals, plan changes, tool errors, and budgets. Add deterministic repeat/no-progress termination; do not rely on a stronger prompt. Verify a repeated-call scenario.

## Tool succeeds but agent ignores it

Check output schema, truncation/artifact summary, observation insertion, context budget, provenance, and plan-step evidence mapping. Ensure the tool result is not silently dropped during compaction.

## Context overflow or quality decay

Measure the actual encoded request, including tools, multimodal/provider state,
and reserved output margin. Inspect the existing context/summary/retry owner before
changing it; do not stack another compaction or fallback layer. Reuse authorized
artifacts/fragments and preserve constraints, numbers/units/exceptions, exact tool
pairs, images, approvals and unmet criteria. An irreducible protected context must
fail explicitly rather than truncate facts or omit required checks. See
`context-management.md` and `document-source-pipelines.md`.

## Unsafe action bypasses approval

Trace every executor entry point. Ensure risk classification uses actual parameters, hard deny precedes allow, approval receipts bind normalized action, and hooks/MCP/subagents call the same permission engine. Add a negative end-to-end test.

## Cannot resume after crash

Check atomic checkpoint/event writes, schema/config fingerprint compatibility, artifact durability, leases, and in-flight side-effect reconciliation. Do not blindly retry non-idempotent tools.

## Memory is irrelevant or leaks

Verify authorization filtering before ranking, scope keys, consent/write policy, conflict handling, retrieval limits, and cache isolation. Rebuild derived indexes after deletion or schema change.

## Model routing is unstable or costly

Separate hard constraints from scoring, pin profile versions, record routing reasons, enforce total budgets, and test outage/fallback. Avoid routing based on unvalidated model self-description.

## Eval passes but production fails

Check scenario coverage, fixture realism, evaluator leakage, model/provider/config drift, tool availability, and trace segmentation. Add the production failure as a versioned regression case after removing sensitive data.

## Capability claimed, but no tool actually works

Treat model self-description or a screenshot as a symptom, not a root-cause log.
Follow installation → loaded configuration → network → underlying tool → Registry/
permission/selection → actual model `tools`/call → matching tool result → UI. Record
the real interpreter and running-process/config identities. A class, package,
`--help`, saved setting or reference fixture proves only that layer. Search HTTP200
with empty/all-failed results is not success; model inference is not a search API;
Playwright import is not browser navigation; tool calling is not JSON-schema model
compatibility. Use [capability-readiness.md](capability-readiness.md).

## Tool catalog error on an ordinary conversation

Check whether ephemeral health or standby facts incorrectly change the pinned
catalog, whether stale probes advertise a retired dependency, and whether an
unavailable optional pack removes unrelated schemas. Preserve real permission and
version fences; do not simply disable catalog validation or mark every tool Ready.

## Buttons, input or streaming UI fail

Map real state/callback ownership and component hierarchy before styling patches.
Check hit testing, validation/busy state, per-request identity, stale callbacks,
theme contrast, modal focus and input-method marked text. Inspect snapshot/event
deduplication, stable message buffers, heavy parsing on the UI thread and scroll
anchoring. Do not fix layout by changing model parameters or replacing backend
authorization. Use [client-experience.md](client-experience.md).

## App cannot connect, or has no accessible window

Compare the actual launch artifact and loaded native/worker identities, not only
source or cache. Separate network endpoint/protocol, native lifecycle/main thread,
OS authorization/signature, lockscreen and automation-tool binding. A direct HTTP
success does not grant the App network access. Use normal permission handoffs;
never edit privacy databases or infer a crash/restart from tool timeout alone.
See [native-cli-client.md](native-cli-client.md).

## A migrated or deleted resource returns

Find every real launcher/config/resolver/worker/installer reference. Confirm the
same private profile/socket and classify active consumers before deletion. A
retired resource needs a persistent gate covering automatic recovery/provision,
not a missing directory or hidden UI. Measure logical versus allocated storage and
preserve data-loss/rollback boundaries. See
[runtime-storage-operations.md](runtime-storage-operations.md).

## Debug evidence order

Reproduce → capture state/trace/config fingerprints → localize the failing boundary → form one falsifiable hypothesis → make the smallest authorized change → run focused then regression tests → inspect trace/diff → document cause and residual risk.

After two similar adjustments without improvement, change the hypothesis or
verification method: inspect the installed version's official API/source/issues,
protocol, layout/state or minimal reproduction. Do not repeatedly tune timeouts,
padding, model context or permissions without new evidence. Keep failed attempts;
do not weaken assertions or relabel blocked/skipped as passed. Continue independent
authorized work when one boundary is blocked. Once affected gates pass and no new
change/failure/risk remains, hand off and clean owned QA rather than restart an
unbounded test/permission loop.
