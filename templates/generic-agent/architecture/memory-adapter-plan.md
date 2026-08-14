# {{PROJECT_NAME}} Memory adapter plan

Implement Memory behind a provider-neutral `MemoryPort`; do not couple domain
contracts to a database or framework SDK.

## Required boundary

- Exactly one canonical store owns versioned Memory records.
- Every operation carries immutable tenant, user, project, and authorization scope.
- Policy checks consent, durable value, sensitivity, and secret material before write.
- Retrieval filters scope and lifecycle status before keyword/vector/graph ranking.
- Store, correction, expiry, deletion, and consent revocation emit a transactional
  lifecycle outbox consumed by every derived index.
- Export is deterministic and carries provenance. Markdown import creates a proposal
  that re-enters policy; it never writes directly.

## Local profile

Use SQLite WAL + FTS5, migration metadata, foreign keys, busy timeout, bounded
retrieval, correction by supersession, soft deletion, expiry, and index rebuild.

## Enterprise adapter plan

Use PostgreSQL as the canonical store. Add Postgres FTS first, then only the measured
vector/graph/framework adapters declared by the Blueprint. Record SecretRefs, backup,
restore, outbox lag, migration, shadow-read comparison, approved cutover, rollback,
and owner/SLO evidence before claiming production readiness.
