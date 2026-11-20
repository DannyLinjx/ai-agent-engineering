# Tool system

A tool is one atomic capability. It does not choose the plan or declare the overall task complete.

## Tool contract

Every tool definition includes:

- globally unique, stable name and version;
- concise model-facing description;
- strict input and output schemas;
- category: read, write, exec, network, database, browser, or communication;
- risk level: low, medium, high, or critical;
- side effects, reversibility, idempotency, and idempotency-key support;
- required scopes and secrets by symbolic reference;
- timeout, output byte cap, concurrency limit, and rate limit;
- cancellation support;
- redaction policy and audit fields;
- owner, tests, and deprecation state.

Use `schemas/tool-manifest.schema.json` and the templates for TypeScript or Python.

## Registry

The registry validates manifests at startup, rejects duplicates and incompatible versions, supports task-scoped allowlists, and exposes only tools relevant to the current task. Keep discovery metadata separate from executable clients. MCP tools pass through the same registry and permission engine.

Registered, installed, configured, enabled, authorized, probed, runtime-bound and
main-product verified are different facts. A stopped verified worker may be
standby rather than Ready; a retired worker must be Disabled and absent from model
schemas. A descriptor or saved config never proves a real handler/model tools
array/result roundtrip. See `capability-readiness.md` for versioned snapshots and
retirement gates. Discover/load only on selection or version/permission change,
not every turn. Empty optional Skill/MCP/knowledge lists must not erase independent
permitted built-ins; missing one dependency must not disable unrelated packs.

## Execution pipeline

1. validate tool name and schema;
2. canonicalize inputs and compute action fingerprint;
3. classify risk using tool metadata plus actual parameters;
4. evaluate permission and approval;
5. reserve budget/concurrency and create tool-run record;
6. execute in the narrowest available sandbox with deadline/cancellation;
7. cap, redact, and validate output;
8. store large output as an artifact;
9. emit structured result, audit record, metrics, and checkpoint.

## Result envelope

Return status, data or artifact reference, human/model summary, timing, retryability, side-effect receipt, warnings, and structured error. Do not expose stack traces, secrets, raw credentials, or unbounded stdout to the model.

## Built-ins

A general engineering agent may need file reads/new artifacts, workspace changes,
isolated code, web search/fetch, fixed API operations or tests. Select these from
the charter and host; a framework/tool list is not authority to enable them all.
Split combined tools when permissions or failure modes differ. File attachments
can work without a Wiki, and Skill/MCP need not be prerequisites for trusted
built-ins. No isolation means the affected execution tool is unavailable, not
permission to silently substitute host exec or install a retired dependency.

## Command and path safety

Resolve paths against the authorized workspace using real paths; reject traversal, symlink escape, device files, and sensitive patterns. Execute commands without implicit shell parsing where possible. When a shell is required, apply an explicit command policy and keep user/model text out of interpolated shell fragments. Use argument arrays and constrained working directories.

## Network, database, browser, and communication

Network tools need destination/IP/redirect/rebinding defenses, egress byte limits,
download validation and the applicable upload authorization. A local inference
endpoint is not automatically a web-search API; loopback differs across host and
container. Select one configured default search provider; do not silently send a
private query to another provider after failure. HTTP200 with empty results/all
upstreams failed is not a successful search. Preserve provenance for private-source
derived queries and authorize their exact outgoing payload/target.

Database tools default to read-only, reviewed operation/templates, parameterized
queries, bounded results and transactions; models cannot choose arbitrary
host/header/SQL. Browser tools isolate profiles/cookies but must also enforce
the real worker/network boundary across subresources, redirects and WebSockets.
Playwright package presence or synthetic DOM clicks do not prove browser navigation
or isolation. API write timeouts need idempotency and outcome reconciliation.
Communication authorization binds the actual recipient/content/side effect; reuse
valid precise prior authority when applicable, and obtain a new approval or user
handoff when policy requires it. For source/files/evidence workflows, read
`document-source-pipelines.md`.

## Tool tests

Test schema rejection, successful action, boundary input, timeout, cancellation, output truncation, transient and permanent error mapping, idempotent retry, denied/asked permissions, secret redaction, workspace escape, and concurrency/rate limits.
