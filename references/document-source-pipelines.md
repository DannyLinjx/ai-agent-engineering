# Scoped sources, document pipelines and evidence

Read this for knowledge-source selection, database-backed Q&A, document Readers,
large-file workflows, bounded evidence or same-file followups. Preserve the existing
source/Reader/ArtifactStore contracts rather than building another RAG/runtime.

## 1. A configured source is not a session grant

Separate source registration, credentials/connection consent, connection verification,
pending selection, confirmed session scope and immutable Run bindings. A selector
may support folder Wiki, local read-only database snapshot or approved remote query
gateway through adapters; its labels do not grant arbitrary filesystem, SQL or URL
access. Projects can organize conversations independently from retrieval scope.

- `Confirm` atomically commits the selected set using the current revision/CAS;
  `Cancel` keeps the previous set. Empty selection means no database/knowledge
  retrieval, never "search every registered source".
- List only sources the current actor may access. Refresh, rebind, detach and
  failure states use the same backend service in settings and conversation UI.
- Each Run pins owner/workspace/source ID/generation/snapshot/digest and permitted
  model origins. Later selection changes cannot rewrite an already running task.
- Rebinding the same source ID makes a new generation. An old answer, summary,
  previous-run chain, cache or evidence reference cannot import facts removed from
  the current scope; require a fresh context/replan when bindings are incompatible.
- Revalidate before reading/decrypting cached content and before/after delivery.
  Source revocation invalidates dependent jobs and derived context, not just a UI
  checkmark. Failed refresh should not silently replace a known working binding.
- Do not scan HOME, infer a default Wiki, or accept runtime/credential roots as
  user knowledge. Validate paths with no-follow/fd ownership controls and protect
  source namespaces, not merely path strings.

Model-visible source handles are opaque scoped references. The host retains actual
paths, credentials and locators privately. Database adapters use reviewed read-only
schemas/templates/operations and parameterized queries; the model cannot choose
arbitrary SQL, tables, host, headers or secret values. Describe actual adapter
support honestly: an HTTP query gateway does not prove native support for every
database's DSN. Local database snapshot handling must account for concurrent
writes/sidecars and stable keys; never mutate a live user database to make a probe
pass.

## 2. One reviewed Reader route per format/task

Reuse the selected default Reader, format registry and worker boundary. Do not
add native/MCP/shell fallback chains for the same business capability merely because
a template includes them. A retired/uninstalled professional parser is Disabled;
raw attachment storage/download may remain allowed, but is not successful parsing.

Identify format using the existing content/signature and archive-safety rules, not
only an untrusted filename. Document parsing, image rendering, OCR/vision, structural
checks, domain-rule execution and business verification are different operations.
A rendered PNG or extracted text does not establish that a model examined the
image or that a design passed an engineering check.

Run CPU-heavy parsing in an owned worker with cancellation/deadline/resource limits,
not on the UI thread or HTTP request handler. Retain the source/Reader/version
fingerprint, extraction limitations, explicit locators and coverage. Reject unsafe
archives/entities/macros or unsupported content rather than silently changing the
Reader route. Preserve generic document tools when a specialist capability is
disabled; missing Wiki or extensions must not disable authorized attachments.

## 3. Programmatic batching and precise fragment reuse

The host advances page/unit/layer/region/object batches and durable cursors. The
model may choose among permitted analysis steps; it must not re-plan every page,
repeat a committed parse or reconstruct a whole large document on each followup.

Bind each independently stored fragment to:

```text
owner/workspace + source generation/snapshot/digest + Reader version
+ locator + original range + explicit offset unit + content digest
+ parent fragment/batch receipt + completion/coverage state
```

Store bounded content separately from metadata/checkpoints. Resume reads the exact
needed fragment/range, not a parent blob subsequently sliced in memory and not an
unbounded archive traversal. Distinguish byte offsets from Unicode codepoints.
Hash and validate actual trusted source bytes; a model-provided artifact ID or
coverage assertion is not authoritative progress.

Commit result receipt, cursor, state and public event atomically. Completed fragments
are reused; duplicate receipts are idempotent and conflicting receipts are rejected.
Splitting failed work preserves parent/source ranges and schedules actual smaller
units; relabeling equal-sized input is not recovery. Pause stops admitting new work
while a safe complete in-flight batch can commit; resume keeps the same Run and
spent budgets. Parent cancel/revoke fences both worker execution and late delivery.

Cache keys include content, Reader/format/version, selected source binding and
relevant model/tool policy. Same-file followups reuse parsed indexes/receipts;
application fragment reuse is not a provider KV-cache claim.

## 4. Retrieval, evidence and coverage

Return bounded search fragments with provenance/cursors, then perform exact reads.
Use fair pagination/merging/deduplication across confirmed sources under explicit
budgets; do not load all source bodies on the home screen or into the model prompt.
When a workflow requires complete rules/catalog enumeration, exhaust the declared
collection or label it incomplete. Top-k retrieval is not exhaustive coverage.

Only operator-reviewed schemas enable executable rule mapping. Unknown schema,
duplicate/unknown fields, nonfinite values, unmapped prose and unsupported conditions
remain untrusted/unmapped data. They cannot become instructions or grant tools.

Evidence includes source version, exact range/locator/object/rule, relevant artifact
and retrieval/extraction time as appropriate. Distinguish parsed, rendered,
examined, validated and unexamined regions. Insufficient evidence yields clarification,
partial/inconclusive findings or refusal, not invented facts or automatic `pass`.
Workflow-specific output formats, confidence labels and verification criteria
come from the current user contract. Do not copy another project's business
workflow or infer a completed assessment from partial coverage.

Client citations resolve only authoritative Evidence/Artifact IDs through the
existing authorization path. Ordinary filenames, `[Evidence 3]` text, model paths
or arbitrary Markdown links cannot create grants. A displayed image must correspond
to the same model-bound artifact/page/layer/region/transformation; an old viewer
response must not replace the currently selected evidence.

## 5. File outputs and selected capability checks

Upload/select/finalize/parse/index/ready are separate facts. Keep existing formats,
multi-file/long-name behavior and server limits; do not add arbitrary UI-only hard
limits to hide performance or state bugs. Large binary previews must not load full
bytes in the client. New outputs are atomic, immutable scoped artifacts with real
bytes/hash/download references. Covering an existing source requires the project's
separate authorized overwrite/version policy.

Verify the selected pipeline with new synthetic fixtures:

- empty extensions/Wiki still allow authorized attachments and new artifacts;
- confirm/cancel/empty/multi-source selection, version conflict, failed refresh,
  detach/rebind and cross-owner/model-origin denial;
- symlink/hardlink/traversal, unsafe document/archive/schema, cursor/range/offset
  mismatch and revoked cache access are rejected before sensitive reads;
- same-file followup reuses the parse/index and reads only the intended fragment;
  many-file/large-file pause/resume/cancel does not replay committed batches;
- unknown rules/facts and reached budgets retain incomplete coverage rather than
  becoming complete checks or global-optimum recommendations;
- artifact generation, authorized download and byte/hash comparison form a real
  main-product flow, not a timer or a fixed-success adapter;
- retired Readers are absent from model schemas and cannot auto-install, while
  permitted generic file/HTTP/model capabilities continue independently.

Record parse/render/model/tool counts and measured input/fragment bytes separately
from tokens, coverage and accuracy. Component or synthetic Reader success is not
live model, visual engineering or full main-client acceptance. Use
`testing-and-evaluation.md` for evidence levels and `runtime-storage-operations.md`
when migrating or retiring the underlying resources.
