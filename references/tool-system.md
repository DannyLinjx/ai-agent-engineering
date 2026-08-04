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

A general engineering agent commonly needs read file, list directory, search files, apply patch/write file, execute command, run Python/JavaScript, web search/fetch, git status/diff, and run tests. Split combined tools when permissions or failure modes differ.

## Command and path safety

Resolve paths against the authorized workspace using real paths; reject traversal, symlink escape, device files, and sensitive patterns. Execute commands without implicit shell parsing where possible. When a shell is required, apply an explicit command policy and keep user/model text out of interpolated shell fragments. Use argument arrays and constrained working directories.

## Network, database, browser, and communication

Network tools need destination allowlists, DNS/rebinding defenses, egress byte limits, download validation, and upload approval. Database tools default to read-only, parameterized queries, bounded results, and transactions. Browser tools isolate profiles and cookies. Communication tools require a final-recipient/content preview and approval before sending.

## Tool tests

Test schema rejection, successful action, boundary input, timeout, cancellation, output truncation, transient and permanent error mapping, idempotent retry, denied/asked permissions, secret redaction, workspace escape, and concurrency/rate limits.
