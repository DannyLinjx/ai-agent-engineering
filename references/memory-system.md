# Memory system

Memory is governed, scoped state—not a transcript dump. Separate short-term session state, long-term durable memory, and user/profile preferences.

## Memory record

Store stable ID, tenant/user/project scope, type, normalized content, source/provenance, confidence, sensitivity, consent basis, created/updated/accessed times, retention/expiry, conflict links, embedding/index version, and deletion state. Encrypt sensitive values and keep credentials out of memory.

## Write policy

Before storing, decide whether the information has durable value, is temporary, duplicates or conflicts with existing memory, is sensitive, requires consent, or should update an existing record. Prefer explicit user confirmation for identity, preferences, and sensitive facts. Do not infer durable personal traits from a single exchange.

## Retrieval

Filter by authorization and scope before ranking. Rank with semantic and keyword relevance, importance, freshness, user/project match, source confidence, and time decay. Return a small set with provenance and confidence. A simple first version can use structured filters, SQLite FTS, and keyword search before vector retrieval.

## Conflict and correction

Never silently overwrite conflicting memory. Link records, prefer authoritative/newer evidence when policy permits, surface uncertainty, and allow user correction. Keep an audit trail without retaining deleted sensitive plaintext.

## Lifecycle

Implement retention, expiration, export, correction, deletion, index rebuild, and consent revocation. Deleting a user/tenant must delete or cryptographically render inaccessible all derived indexes and cached context.

## Tests

Test that temporary facts are not stored, durable facts are stored with consent, new sessions retrieve only relevant records, duplicates merge, conflicts remain visible, decay changes ranking, sensitive values are rejected/redacted, tenant scopes do not cross, and deletion propagates.
