# Memory system

Memory is governed, scoped state—not a transcript dump. Separate short-term session state, long-term durable memory, user/profile preferences and verified reusable experience. Canonical Run status remains owned by its task repository; memory or learned policy cannot mark a Run completed or turn experience into a business fact. Preserve the project's declared layer semantics: record enums, reflection jobs and context-pressure stages do not independently define new Memory layers.

For profile selection, SQLite/FTS5 implementation, enterprise adapters, and safe
migration/cutover, also read `memory-deployment.md` and use
`../assets/memory-platform.mmd` as the lifecycle map.

## Memory record

Store stable ID, tenant/user/project scope, type, normalized content, source/provenance, confidence, sensitivity, consent basis, created/updated/accessed times, retention/expiry, conflict links, embedding/index version, and deletion state. Encrypt sensitive values and keep credentials out of memory.

## Write policy

Before storing, decide whether the information has durable value, is temporary, duplicates or conflicts with existing memory, is sensitive, requires consent, or should update an existing record. Obtain the required consent for identity, preferences and sensitive facts; apply an existing precise consent without repeatedly asking. A correction for this task or an implicit negative rating does not authorize future/workspace learning. Do not infer durable personal traits from a single exchange. Verified experience needs actual accepted receipts and provenance, not the model's statement that it succeeded. See `prompt-policy-learning.md` when reusable feedback may modify mutable policy.

## Retrieval

Filter by authorization and scope before ranking and before decrypting/delivering cached derivatives. Rank with semantic and keyword relevance, importance, freshness, user/project match, source confidence, and time decay. Return a small relevant set with provenance and confidence, as lower-trust context rather than system authority; current explicit instructions win. A simple first version can use the project's structured/keyword baseline before vector retrieval. Do not load whole memory files or save hidden reasoning.

## Conflict and correction

Never silently overwrite conflicting memory. Link records, prefer authoritative/newer evidence when policy permits, surface uncertainty, and allow user correction. Keep an audit trail without retaining deleted sensitive plaintext.

## Lifecycle

Implement retention, expiration, export, correction, deletion, index rebuild, and consent revocation. Forget/revoke must invalidate subsequent model context, summaries, ancestor-derived answers, caches and indexes; retaining a source reference is not continuing permission to reveal it. Deleting a user/tenant must delete or cryptographically render inaccessible the applicable records and derivatives according to retention policy. Keep audit metadata without retaining revoked sensitive plaintext.

The Python reference scaffold implements this local boundary with frozen contracts,
`MemoryPolicy`, `SQLiteMemoryStore`, a transactional lifecycle/index outbox,
`MemoryRetriever`, deterministic JSON export, and Markdown import proposals. It uses
only the Python standard library; it is a runnable prototype baseline, not evidence
that an enterprise database or external adapter is installed or verified.

## Tests

Test that temporary facts are not stored, durable facts are stored with consent, new sessions retrieve only relevant records, duplicates merge, conflicts remain visible, decay changes ranking, sensitive values are rejected/redacted, tenant scopes do not cross, and deletion propagates.

Add restart persistence, authorization-before-ranking, deterministic export,
transactional outbox, index rebuild, backup restore, shadow-read comparison, and
rollback tests when the selected profile includes those behaviors. Optional vector,
graph, or Mem0 adapters are `not_applicable` until selected and configured.
