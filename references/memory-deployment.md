# Memory platform and deployment

Use this reference to choose the smallest Memory profile and to plan an upgrade from
a local prototype to an enterprise service. Read `memory-system.md` for the record,
write, retrieval, conflict, and lifecycle rules.

## Profile decision

The table contains reference database choices for new deployments, not a mandate
to migrate an existing application. Preserve its encryption, payload boundaries
and user-approved readable-file semantics unless migration is part of the task.

| Profile | Canonical store | Derived indexes | Default use |
|---|---|---|---|
| `local` | SQLite | SQLite FTS5 | prototype, local user, fast recovery |
| `hybrid` | PostgreSQL | Postgres FTS plus optional vector/graph adapter | shared service growing beyond one process |
| `enterprise` | PostgreSQL | governed Postgres FTS, optional pgvector/Redis/Qdrant/Milvus/Weaviate/Mem0 and optional Neo4j | multi-user production with backup, SLO, migration, and audit |

Exactly one canonical authority owns each logical Memory record. This does not
require one physical database for every data class. Select reviewed storage
adapters and encryption/consent rules for each class. Document ownership,
versioning, atomicity and lifecycle for
each class; two writable authorities for the same record remain prohibited. Vector
databases, graph stores and frameworks are projections/adapters. Markdown is an
export/import boundary in the bundled SQLite prototype, but may be the selected
canonical representation for an existing scoped record type; it is not permission
to bypass policy, encryption requirements or actor/source isolation.

For a new database-backed prototype, SQLite + FTS5 is a reference starting point.
For an existing file/encrypted-payload design, retain its selected store/adapter and
mark unavailable scaffold implementations as planned, not generated or verified.
Do not choose infrastructure solely because a template lacks its adapter. Add vector retrieval only when keyword/structured baselines
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

Require applicable authorization before system dependency installation, network exposure,
secret configuration, live-data migration, backup changes, or production cutover.
Reuse an existing authorization only within its actual action/data/target/risk scope;
a profile or download permission is not authority to migrate user data or emit tracing.
Verify tenant filters, encryption, retention jobs, backup restore, index rebuild,
outbox lag, migration reconciliation, SLOs, and rollback before claiming readiness.

Generate the deterministic non-mutating topology plan with:

```bash
python scripts/plan_memory_deployment.py \
  --request examples/memory-deployment-request.json \
  --output ./memory-deployment-plan.json
```

The planner writes only the requested plan file. It does not create a database,
Compose file, `.env`, service process, account, network listener, or credential.

Validate the generated contract with:

```bash
python scripts/validate_memory_manifest.py \
  --manifest <agent>/factory/memory-manifest.json --json
```

The architecture is summarized in `../assets/memory-platform.mmd`; examples are
`../examples/local-memory-agent-blueprint.json` and
`../examples/browser-enterprise-agent-blueprint.json`.
