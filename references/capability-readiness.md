# Capability wiring, readiness and retirement

Read when implementing built-ins/extensions, diagnosing misleading capability
claims, configuring a provider, or disabling/uninstalling a backend. Registry
presence is descriptive; effective execution authority remains host-owned.

## Map actual integration before patching

Create a source-to-integration map with the existing entry, running process,
worker interpreter, configuration/secret resolution, Registry factory, selection,
permission filter, model-request serialization, executor, receipt/artifact storage,
tool-result message insertion and client projection. Locate real functions and
tests; record gaps instead of guessing file names or endpoint routes. Do not accept
a reference adapter in `design/`, an import, package installation or successful
`--help` as evidence that the primary process uses it.

Trace a synthetic request through:

```text
registered → enabled → authorized → selected → model wire schema
→ actual tool_call → validated execution → receipt/artifact
→ matching tool result in the same model session → user result
```

Record names/schema hashes, catalog/config/permission versions, request/run IDs,
safe status and timing. Do not log raw prompt, file body, credentials or hidden
reasoning. Host context injects actor/scope/grants/deadline/cancel; model parameters
cannot grant any of them. Built-in factories are independent of optional Skill,
MCP or knowledge mounts unless a declared dependency genuinely requires one.

## Readiness is a vector, not one boolean

Track applicable facts separately: selected, registered/reviewed, installed,
configured, credentials-present, authorized, service-reachable, probe-verified,
runtime-bound, model-called and primary-product-verified. Include reason, version,
verification time/scope and health expiry. Distinguish unavailable, not-configured,
permission-required, not-probed, standby, ready, blocked, disabled and retired.

Saving settings is not Ready. A valid previous probe is not evidence for a changed
configuration/model/tool schema/permission version. A stopped on-demand service may
be available in verified standby without falsely reporting running/Ready. Reading
a capability snapshot must not start that service or install anything. Conversely,
standby/disabled should not make an unrelated no-tool greeting fail admission.

Generate model-visible schemas and capability self-description from this shared
snapshot. Recompute on version changes rather than rediscovering/loading skills
every turn. Filter only capabilities affected by a missing dependency; ordinary
file access does not require a Wiki, and disabling code need not disable HTTP/API.
Never expose test Echo handlers or pretend a stub is a real business capability.

## Real probes and provider-specific failure classes

| Capability | Required proof and common false positive |
|---|---|
| Search | Correct selected provider/endpoint and JSON schema, HTTP status, nonempty usable results, upstream errors and latency; HTTP200 empty/all-engines-failed is not success |
| URL fetch | Actual authorized response, content/range/time/hash; a search snippet or known URL is not a fetched document |
| Code | Real approved isolated execution, exit/output quotas, actual artifact bytes/hash and Stop cleanup; package import or host execution is not sandbox proof |
| Browser | Matching package/browser/worker environment, real context/navigation/interaction/cancel and egress negatives; `set_content` proves only DOM behavior |
| API | Registered fixed operation, validated parameters, actual response/schema/redaction and result return; one public read does not establish enterprise integration or safe writes |
| Model | Exact protocol/profile and required features; tool calling does not prove JSON-schema structured output, streaming, vision or remote-stop confirmation |
| MCP/Plugin | Selected transport/adapter, negotiated schema, permissions and actual invocation; offline schema tests are not live SDK or remote-service acceptance |

Keep search and model inference providers distinct; a local model's tool calling
does not supply a search index/API key. Use one explicitly selected search provider;
do not silently forward private queries to another on failure. Diagnose 401/403/429,
HTML-instead-of-JSON, timeout, DNS/proxy and upstream outage at the failing boundary,
not by increasing model context. An exact operator loopback exception is not an
arbitrary-network grant. Private-source-derived queries still require egress
authorization; a bounded public task can reuse its already granted scope.

## Persistent disable and retirement

Treat operator retirement as a lifecycle event, distinct from accidental outage.
Before uninstalling, inspect actual users, active handles, receipts, versions,
container/volume or external side effects and the authorized data-loss boundary.
Record the later decision as superseding any former installation/preservation plan.

The disable gate must cover:

1. capability snapshots and model schemas;
2. execution, planning and direct adapter calls;
3. probes and automatic recovery/reconciliation that could start a dependency;
4. startup, installers/provisioners, health repair and scheduled jobs;
5. cached probe/config/permission generations and in-flight/late deliveries.

Fail with a fixed disabled/retired reason before resource creation or external
effect. Do not silently convert a retired sandbox into host execution or substitute
another provider with broader data flow. Retain unrelated capabilities and useful
lightweight contracts, and document whether an operator-only diagnostic is harmless
and non-provisioning. Re-enablement/reinstallation needs current authorization,
compatible resources and new verification; restoring an old flag is not recovery of
deleted data. See [runtime-storage-operations.md](runtime-storage-operations.md).

## Acceptance evidence

Prove both the positive path and invalidation: empty optional extensions, correct
model wire schemas, tool results returned to the original session, config change,
permission/source revoke, dependency stop, stale probe, disable and uninstall.
Verify a primary-product natural-language request when that is promised. Isolated
tool/CLI/fixture success cannot be promoted to that layer. Preserve the old failure
and report each final disposition using [testing-and-evaluation.md](testing-and-evaluation.md).
