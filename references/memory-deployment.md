# Memory platform and deployment

Use this reference to choose the smallest Memory profile and to plan an upgrade from
a local prototype to an enterprise service. Read `memory-system.md` for the record,
write, retrieval, conflict, and lifecycle rules.

## Profile decision

| Profile | Canonical store | Derived indexes | Default use |
|---|---|---|---|
| `local` | SQLite | SQLite FTS5 | prototype, local user, fast recovery |
| `hybrid` | PostgreSQL | Postgres FTS plus optional vector/graph adapter | shared service growing beyond one process |
| `enterprise` | PostgreSQL | governed Postgres FTS, optional pgvector/Redis/Qdrant/Milvus/Weaviate/Mem0 and optional Neo4j | multi-user production with backup, SLO, migration, and audit |

Exactly one canonical store owns each Memory record. Vector databases, graph stores,
and frameworks are projections or adapters, never competing sources of truth. Markdown
is an explicit human-readable export/import boundary, not a concurrent database.

Start with SQLite + FTS5 unless scale, availability, tenancy, or an already-operated
platform requires more. Add vector retrieval only when keyword/structured baselines
fail a measured recall criterion. Add graph storage only for a declared relationship
query and acceptance scenario. Add Mem0 or another framework only behind `MemoryPort`;
do not let it bypass consent, scope, provenance, correction, deletion, or audit policy.

## Prototype path

The local implementation should provide:

1. immutable scoped Memory contracts and deterministic write policy;
2. SQLite WAL, migrations, foreign keys, busy timeout, lifecycle events, and a
   transactional index outbox;
3. authorization and active/expiry filtering before FTS candidates and ranking;
4. bounded results with score components, source, evidence, and confidence;
5. correction by supersession, soft deletion, expiry, deterministic JSON export,
   and Markdown proposals that re-enter policy evaluation.

Credentials and secret-shaped content are rejected before persistence. Deletion and
consent revocation propagate to every derived index and cache.

## Enterprise evolution

Generate a deployment plan before changing infrastructure. A safe migration is:

```text
validate backup/restore → sample export/import → bulk backfill → dual-write outbox
→ shadow reads and compare → human-approved cutover → monitored rollback window
```

The plan records dependencies, SecretRefs, owners, approval gates, validation,
migration, cutover, and rollback. The Factory only writes this plan. `guided_install`
and `end_to_end` mean the implementing Agent may later guide or execute approved
steps; they never grant installation, credential, network, migration, or production
authority by themselves.

Require explicit approval before system dependency installation, network exposure,
secret configuration, live-data migration, backup changes, or production cutover.
Verify tenant filters, encryption, retention jobs, backup restore, index rebuild,
outbox lag, migration reconciliation, SLOs, and rollback before claiming readiness.

Validate the generated contract with:

```bash
python scripts/validate_memory_manifest.py \
  --manifest <agent>/factory/memory-manifest.json --json
```

The architecture is summarized in `../assets/memory-platform.mmd`; examples are
`../examples/local-memory-agent-blueprint.json` and
`../examples/browser-enterprise-agent-blueprint.json`.
