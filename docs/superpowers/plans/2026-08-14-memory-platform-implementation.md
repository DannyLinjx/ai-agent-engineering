# Memory Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the in-memory demonstration with a governed SQLite/FTS5 prototype template and add non-mutating enterprise Memory selection, migration, deployment, and validation artifacts.

**Architecture:** Keep `MemoryManager` as a compatibility facade over a `MemoryPort`, deterministic policy, SQLite canonical store, and bounded retrieval service. Enterprise services remain adapter declarations and deployment plans; exactly one canonical store owns records and every derived index follows lifecycle events.

**Tech Stack:** Python 3.11 standard library, `sqlite3`, SQLite FTS5, JSON, `unittest`.

## Global Constraints

- Modify only `/Users/danny/Documents/skills/ai-agent-engineering`.
- Follow strict TDD for every Python behavior.
- SQLite is the local canonical source; Markdown is explicit import/export only.
- Credentials and secret-like data are rejected before persistence.
- Authorization scope is applied before returning or ranking Memory.
- External databases and Mem0 remain optional and are never installed or contacted by core tests.

---

## File map

- `templates/python-agent/src/agent_runtime/memory/contracts.py`: immutable Memory types and query/result contracts.
- `templates/python-agent/src/agent_runtime/memory/policy.py`: consent, sensitivity, secret, durable-value, conflict decisions.
- `templates/python-agent/src/agent_runtime/memory/sqlite_store.py`: migrations, canonical writes, lifecycle, outbox, export.
- `templates/python-agent/src/agent_runtime/memory/retrieval.py`: structured and FTS5 retrieval/ranking.
- `templates/python-agent/src/agent_runtime/memory/__init__.py`: public API.
- `templates/python-agent/src/agent_runtime/memory.py`: compatibility import facade.
- `templates/python-agent/tests/test_memory_platform.py`: executable candidate behavior.
- `templates/memory.config.json`: provider-neutral settings.
- `templates/generic-agent/architecture/memory-adapter-plan.md`: language-neutral port and lifecycle contract.
- `scripts/plan_memory_deployment.py`: pure plan generator.
- `examples/memory-deployment-request.json`: deterministic planner input.
- `tests/test_memory_platform_templates.py`: Skill-level scaffold and planner tests.

### Task 1: Define the Memory contracts and policy

**Files:**
- Create: `templates/python-agent/src/agent_runtime/memory/contracts.py`
- Create: `templates/python-agent/src/agent_runtime/memory/policy.py`
- Create: `templates/python-agent/src/agent_runtime/memory/__init__.py`
- Create: `templates/python-agent/tests/test_memory_platform.py`
- Modify: `templates/python-agent/src/agent_runtime/memory.py`

**Interfaces:**
- Produces: `MemoryScope`, `MemoryRecord`, `MemoryQuery`, `MemorySearchResult`, `MemoryDecision`.
- Produces: `MemoryPolicy.evaluate(record: MemoryRecord) -> MemoryDecision`.

- [ ] **Step 1: Write failing policy tests**

Cover literal outcomes:

```python
def test_policy_rejects_record_without_consent():
    decision = MemoryPolicy().evaluate(record(consent_basis="none"))
    assert decision.action == "reject"
    assert decision.reason == "consent_required"

def test_policy_rejects_secret_material():
    decision = MemoryPolicy().evaluate(record(content={"api_key": "sk-test-value"}))
    assert decision.reason == "secret_material"
```

- [ ] **Step 2: Verify RED**

Run the scaffolded test from a temporary Python project with `PYTHONPATH=src`.

Expected: import failure because the Memory package does not exist.

- [ ] **Step 3: Implement immutable contracts and minimal policy**

Use frozen dataclasses. `MemoryRecord` includes IDs/scopes, type, dict content, summary, source, evidence refs, confidence, importance, sensitivity, consent basis, policy version, timestamps, lifecycle status, conflict/supersession links, and optional embedding metadata.

Policy returns one of `accept`, `reject`, or `needs_confirmation`; it never mutates the record.

- [ ] **Step 4: Verify GREEN**

Run the focused candidate tests.

Expected: PASS.

- [ ] **Step 5: Preserve compatibility imports**

`agent_runtime.memory` re-exports `MemoryManager`, `MemoryRecord`, and the new public types so existing generated imports do not break.

- [ ] **Step 6: Commit contracts and policy**

```bash
git add templates/python-agent/src/agent_runtime/memory.py templates/python-agent/src/agent_runtime/memory templates/python-agent/tests/test_memory_platform.py
git commit -m "feat(memory): define governed memory contracts and policy"
```

### Task 2: Implement the SQLite canonical store and lifecycle

**Files:**
- Create: `templates/python-agent/src/agent_runtime/memory/sqlite_store.py`
- Modify: `templates/python-agent/tests/test_memory_platform.py`

**Interfaces:**
- Produces: `SQLiteMemoryStore(path: Path)`.
- Methods: `put`, `get`, `list`, `soft_delete`, `correct`, `expire_due`, `export_records`, `pending_index_events`, `mark_index_event_applied`.

- [ ] **Step 1: Write failing persistence and isolation tests**

Test a fresh database, reopen it, retrieve Alice's record, and assert Bob gets `None`. Assert correction creates a new record with `supersedes_id` while the original becomes `superseded`.

- [ ] **Step 2: Verify RED**

Run the focused SQLite tests.

Expected: FAIL because `SQLiteMemoryStore` does not exist.

- [ ] **Step 3: Implement migrations and connection settings**

On connect execute:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=10000;
```

Create `memory_schema_meta`, `memory_records`, `memory_relations`, `memory_events`, and `memory_index_outbox`. All reads include tenant and user predicates.

- [ ] **Step 4: Implement lifecycle transactions**

`put`, correction, expiry, and deletion append a lifecycle event and outbox record in the same transaction. Secret rejection remains in policy before `put`.

- [ ] **Step 5: Verify GREEN**

Run candidate Memory tests.

Expected: persistence, isolation, correction, expiry, deletion, and reopen tests pass.

- [ ] **Step 6: Commit SQLite lifecycle**

```bash
git add templates/python-agent/src/agent_runtime/memory/sqlite_store.py templates/python-agent/tests/test_memory_platform.py
git commit -m "feat(memory): add scoped sqlite lifecycle store"
```

### Task 3: Add FTS5 retrieval and bounded ranking

**Files:**
- Create: `templates/python-agent/src/agent_runtime/memory/retrieval.py`
- Modify: `templates/python-agent/src/agent_runtime/memory/sqlite_store.py`
- Modify: `templates/python-agent/tests/test_memory_platform.py`

**Interfaces:**
- Produces: `MemoryRetriever.search(query: MemoryQuery) -> list[MemorySearchResult]`.
- Search order: scope filter, active/expiry filter, FTS candidates, deterministic score, bounded return.

- [ ] **Step 1: Write failing retrieval tests**

Insert relevant, stale, expired, and cross-user records. Assert only active in-scope results return, relevance beats unrelated recency, and `limit=2` returns exactly two.

- [ ] **Step 2: Verify RED**

Run retrieval tests.

Expected: FAIL because no retriever exists.

- [ ] **Step 3: Implement the FTS5 index and query**

Create an FTS5 table over record ID, summary, and normalized text. Treat scope columns as unindexed metadata and join to canonical records with tenant/user predicates. Parameterize every SQL value and cap limits at 50.

- [ ] **Step 4: Implement hand-derived scoring**

Combine normalized FTS rank with stored importance, confidence, and a bounded freshness factor. Include source, evidence refs, confidence, and score components in the result; do not return raw internal SQL rank alone.

- [ ] **Step 5: Verify GREEN and mutation cases**

Run all Memory tests, then temporarily disable the user predicate and confirm the isolation test fails before restoring it.

Expected: final run PASS.

- [ ] **Step 6: Commit retrieval**

```bash
git add templates/python-agent/src/agent_runtime/memory templates/python-agent/tests/test_memory_platform.py
git commit -m "feat(memory): add scoped fts5 retrieval"
```

### Task 4: Add Memory configuration and Markdown import/export boundary

**Files:**
- Create: `templates/memory.config.json`
- Create: `templates/generic-agent/architecture/memory-adapter-plan.md`
- Modify: `templates/python-agent/src/agent_runtime/memory/sqlite_store.py`
- Modify: `templates/python-agent/tests/test_memory_platform.py`
- Modify: `schemas/agent-config.schema.json`
- Modify: `templates/agent-config.yaml`

**Interfaces:**
- Produces deterministic JSON export sorted by scope, created time, and ID.
- Markdown export is derived and carries record IDs and provenance.
- Import creates proposals, never bypasses policy.

- [ ] **Step 1: Write failing export/import tests**

Assert two exports of unchanged data are byte-identical, deleted records are excluded by default, and Markdown import returns proposals requiring policy evaluation.

- [ ] **Step 2: Verify RED**

Run focused export/import tests.

Expected: FAIL because export/import is missing.

- [ ] **Step 3: Implement deterministic export and proposal import**

Use JSON as the machine contract. Markdown contains front matter with `record_id`, `memory_type`, `source`, and `exported_from`; edited Markdown is parsed into a new proposal with `source=markdown_import`.

- [ ] **Step 4: Add strict config choices**

Schema and template declare profile, canonical store, keyword/vector/graph indexes, framework, database URL/SecretRef, and Markdown mode. Raw credentials are forbidden.

- [ ] **Step 5: Verify GREEN and scaffold acceptance**

Run candidate Memory tests and the existing Python scaffold acceptance test.

Expected: PASS.

- [ ] **Step 6: Commit configuration and export**

```bash
git add schemas/agent-config.schema.json templates/agent-config.yaml templates/memory.config.json templates/generic-agent/architecture/memory-adapter-plan.md templates/python-agent
git commit -m "feat(memory): add portable config and governed export"
```

### Task 5: Generate non-mutating enterprise deployment and migration plans

**Files:**
- Create: `scripts/plan_memory_deployment.py`
- Create: `examples/memory-deployment-request.json`
- Create: `tests/test_memory_platform_templates.py`
- Modify: `scripts/validate_skill_structure.py`

**Interfaces:**
- CLI: `python scripts/plan_memory_deployment.py --request <json> --output <json>`.
- Pure function: `build_deployment_plan(request: dict[str, Any]) -> dict[str, Any]`.

- [ ] **Step 1: Write failing planner tests**

Assert local requests select SQLite/FTS5 with no services, hybrid requests select PostgreSQL/pgvector, Redis is optional, Neo4j requires a graph acceptance case, and every plan sets installation/deployment authority false.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_memory_platform_templates.MemoryPlatformTemplateTests.test_planner_selects_minimal_topology -v`

Expected: FAIL because the script is absent.

- [ ] **Step 3: Implement request validation and topology selection**

The request includes profile, users, tenancy, expected records, concurrency, latency target, availability target, graph queries, managed/self-hosted preference, data class, and engagement. Selection is deterministic and emits reasons, dependencies, ports, volumes, SecretRefs, backup, migration, validation, cutover, rollback, and approval gates.

- [ ] **Step 4: Add destructive-boundary tests**

Run the planner in a temporary directory and assert it creates only the named output, no target database, no `.env`, no Compose file, and no network process.

- [ ] **Step 5: Verify GREEN**

Run planner tests and structure validation.

Expected: PASS.

- [ ] **Step 6: Commit enterprise planning**

```bash
git add scripts/plan_memory_deployment.py examples/memory-deployment-request.json tests/test_memory_platform_templates.py scripts/validate_skill_structure.py
git commit -m "feat(memory): plan governed enterprise deployment"
```

### Task 6: Verify the generated Memory candidate end to end

**Files:**
- Modify: `tests/test_memory_platform_templates.py`
- Modify: `references/memory-system.md`
- Modify: `references/memory-deployment.md`

**Interfaces:**
- Generated Python candidate runs its own Memory suite with only the standard library.

- [ ] **Step 1: Add a failing scaffolded-candidate acceptance test**

Scaffold to a temporary directory, then execute `python -m unittest discover -s tests -v` with `PYTHONPATH=src`. Assert zero failures and that no external database package is imported by the local profile.

- [ ] **Step 2: Verify RED before final wiring**

Expected: FAIL until all Memory template files and package exports are copied correctly.

- [ ] **Step 3: Fix only the missing scaffold/package wiring**

Do not add new Memory behavior in this step.

- [ ] **Step 4: Run full verification**

Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_skill_structure.py --skill . --json
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit the Memory acceptance closure**

```bash
git add tests references templates
git commit -m "test(memory): verify generated local memory candidate"
```
