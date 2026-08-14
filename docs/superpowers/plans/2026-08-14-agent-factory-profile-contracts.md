# Agent Factory Profile Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add backward-compatible Browser Experience, Memory, and Delivery profiles to Agent Blueprint and make the Factory emit deterministic, validated manifests without installing or deploying anything.

**Architecture:** Extend the existing hand-validated Blueprint contract with optional profile sections that normalize to safe defaults. Keep profile derivation inside `create_agent_from_blueprint.py`, emit language-neutral artifacts, and compose optional scaffolds only through the existing non-overwriting project generator.

**Tech Stack:** Python 3.11 standard library, JSON Schema documents, `unittest`, existing Factory scripts.

## Global Constraints

- Modify only `/Users/danny/Documents/skills/ai-agent-engineering`.
- Version 1.0 Blueprints without the new sections remain valid and normalize to headless, disabled local Memory, and plan-only delivery.
- Factory scripts never install dependencies, start services, open a browser, connect credentials, migrate live data, or deploy.
- A generated artifact is never reported as verified or production ready without executable evidence.
- Preserve non-empty target protection and pre-write inline-credential rejection.

---

## File map

- `schemas/agent-blueprint.schema.json`: optional profile contract.
- `schemas/experience-manifest.schema.json`: generated browser plan contract.
- `schemas/memory-manifest.schema.json`: generated Memory plan contract.
- `schemas/deployment-plan.schema.json`: non-mutating delivery plan contract.
- `schemas/browser-run-event.schema.json`: safe browser event allowlist.
- `scripts/create_agent_from_blueprint.py`: normalization, validation, derivation, artifacts.
- `scripts/scaffold_agent_project.py`: safe optional overlay composition.
- `scripts/validate_experience_manifest.py`: semantic Experience validation.
- `scripts/validate_memory_manifest.py`: semantic Memory validation.
- `assets/capability-catalog.json`: new capabilities.
- `templates/agent-blueprint.json`: legacy-compatible default example.
- `examples/browser-enterprise-agent-blueprint.json`: operations-console example.
- `examples/local-memory-agent-blueprint.json`: local Memory example.
- `tests/test_factory_profiles.py`: behavioral regression and profile tests.
- `scripts/validate_skill_structure.py`: required-resource inventory.
- `SKILL.md`, `README.md`, and references: progressive-disclosure routing.

### Task 1: Lock backward-compatible Blueprint behavior

**Files:**
- Create: `tests/test_factory_profiles.py`
- Modify: `schemas/agent-blueprint.schema.json`
- Modify: `scripts/create_agent_from_blueprint.py`

**Interfaces:**
- Produces: `normalize_profiles(value: dict[str, Any]) -> dict[str, Any]`
- Produces: normalized `experience`, `memory`, and `delivery` objects.

- [ ] **Step 1: Write the failing default-normalization test**

```python
def test_legacy_blueprint_normalizes_to_safe_profiles() -> None:
    blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text())
    normalized = FACTORY.normalize_profiles(blueprint)
    assert normalized["experience"] == {
        "profile": "headless", "reference_stack": "none",
        "auth": "none", "realtime": "none", "surfaces": [],
    }
    assert normalized["memory"]["enabled"] is False
    assert normalized["memory"]["profile"] == "local"
    assert normalized["delivery"] == {"engagement": "plan_only"}
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_legacy_blueprint_normalizes_to_safe_profiles -v`

Expected: FAIL because `normalize_profiles` does not exist.

- [ ] **Step 3: Add optional JSON Schema sections and minimal normalization**

Implement exact enums:

```python
EXPERIENCE_PROFILES = {"headless", "browser_chat", "operations_console"}
REFERENCE_STACKS = {"none", "react_fastapi"}
AUTH_PROFILES = {"none", "local_account", "server_session", "oidc"}
REALTIME_PROFILES = {"none", "sse", "websocket"}
MEMORY_PROFILES = {"local", "hybrid", "enterprise"}
DELIVERY_ENGAGEMENTS = {"plan_only", "guided_install", "end_to_end"}

def normalize_profiles(value: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(value)
    normalized["experience"] = {
        "profile": "headless", "reference_stack": "none",
        "auth": "none", "realtime": "none", "surfaces": [],
        **(value.get("experience") if isinstance(value.get("experience"), dict) else {}),
    }
    normalized["memory"] = {
        "enabled": False, "profile": "local", "canonical_store": "sqlite",
        "keyword_index": "sqlite_fts5", "vector_index": "none",
        "graph_store": "none", "framework": "native",
        **(value.get("memory") if isinstance(value.get("memory"), dict) else {}),
    }
    normalized["delivery"] = {
        "engagement": "plan_only",
        **(value.get("delivery") if isinstance(value.get("delivery"), dict) else {}),
    }
    return normalized
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_legacy_blueprint_normalizes_to_safe_profiles -v`

Expected: PASS.

- [ ] **Step 5: Run the existing Factory tests**

Run: `python -m unittest tests.test_scripts.SkillScriptTests.test_agent_factory_plan_is_deterministic_and_non_mutating tests.test_scripts.SkillScriptTests.test_agent_factory_apply_supports_generic_scaffold -v`

Expected: PASS.

- [ ] **Step 6: Commit the contract slice**

```bash
git add schemas/agent-blueprint.schema.json scripts/create_agent_from_blueprint.py tests/test_factory_profiles.py
git commit -m "feat(factory): add backward-compatible agent profiles"
```

### Task 2: Validate profile combinations and derive capabilities

**Files:**
- Modify: `tests/test_factory_profiles.py`
- Modify: `scripts/create_agent_from_blueprint.py`
- Modify: `assets/capability-catalog.json`

**Interfaces:**
- Consumes: `normalize_profiles`.
- Produces: `derive_profile_capabilities(value: dict[str, Any]) -> set[str]`.
- Produces: validation issues with stable `code`, `message`, and `path`.

- [ ] **Step 1: Write failing profile conflict tests**

Add table-driven cases asserting these issue codes:

```python
cases = [
    ({"profile": "operations_console", "auth": "none"}, "experience-auth-required"),
    ({"profile": "browser_chat", "reference_stack": "none"}, "experience-stack-required"),
]
```

Add a Memory case asserting enterprise + SQLite returns `enterprise-canonical-store`.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_invalid_profile_combinations_are_blocked -v`

Expected: FAIL because no profile-specific issues are emitted.

- [ ] **Step 3: Implement derivation and semantic validation**

Use literal capability sets:

```python
BROWSER_CHAT_CAPABILITIES = {
    "browser-experience", "session", "checkpoint", "security", "permissions", "verification",
}
OPERATIONS_CONSOLE_CAPABILITIES = BROWSER_CHAT_CAPABILITIES | {
    "observability", "operations", "multi-user-isolation", "audit-and-artifacts", "realtime-events",
}
MEMORY_CAPABILITIES = {"memory", "session", "checkpoint", "memory-governance"}
ENTERPRISE_MEMORY_CAPABILITIES = MEMORY_CAPABILITIES | {
    "operations", "multi-user-isolation", "memory-migration", "backup-and-recovery",
}
```

Reject only incompatible combinations. Do not reject a valid unimplemented adapter; mark it planned later.

- [ ] **Step 4: Verify GREEN and catalog consistency**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_invalid_profile_combinations_are_blocked tests.test_factory_profiles.FactoryProfileTests.test_profiles_derive_required_capabilities -v`

Expected: PASS.

- [ ] **Step 5: Run all Factory tests**

Run: `python -m unittest tests.test_scripts tests.test_factory_profiles -v`

Expected: PASS.

- [ ] **Step 6: Commit semantic validation**

```bash
git add assets/capability-catalog.json scripts/create_agent_from_blueprint.py tests/test_factory_profiles.py
git commit -m "feat(factory): derive governed experience and memory capabilities"
```

### Task 3: Emit and validate the three Factory manifests

**Files:**
- Create: `schemas/experience-manifest.schema.json`
- Create: `schemas/memory-manifest.schema.json`
- Create: `schemas/deployment-plan.schema.json`
- Create: `schemas/browser-run-event.schema.json`
- Create: `scripts/validate_experience_manifest.py`
- Create: `scripts/validate_memory_manifest.py`
- Modify: `scripts/create_agent_from_blueprint.py`
- Modify: `tests/test_factory_profiles.py`

**Interfaces:**
- Produces: `_experience_manifest(blueprint, recipe) -> dict[str, Any]`.
- Produces: `_memory_manifest(blueprint, recipe) -> dict[str, Any]`.
- Produces: `_deployment_plan(blueprint, recipe) -> dict[str, Any]`.
- Validators exit 0 on valid input and 1 on semantic violations.

- [ ] **Step 1: Write a failing manifest-generation test**

Apply the browser enterprise example to a temporary target and assert:

```python
for name in ("experience-manifest.json", "memory-manifest.json", "deployment-plan.json"):
    assert (target / "factory" / name).is_file()
deployment = json.loads((target / "factory/deployment-plan.json").read_text())
assert deployment["installation_allowed"] is False
assert deployment["deployment_allowed"] is False
```

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_apply_emits_profile_manifests_without_install_authority -v`

Expected: FAIL because the files do not exist.

- [ ] **Step 3: Add strict schemas and deterministic builders**

Use sorted arrays, stable key ordering through `_common.write_json`, no timestamps, and no host-derived paths inside hash inputs. Deployment Plan records `engagement`, `installation_allowed`, `deployment_allowed`, `dependencies`, `approval_gates`, `validation_commands`, `cutover`, and `rollback`.

- [ ] **Step 4: Implement validators**

Experience validator checks profile/stack/auth/realtime compatibility and safe event names. Memory validator checks canonical-store/profile compatibility, one canonical store, and optional adapter status. Both reject raw credential-shaped keys and values.

- [ ] **Step 5: Verify GREEN and deterministic output**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_apply_emits_profile_manifests_without_install_authority tests.test_factory_profiles.FactoryProfileTests.test_profile_plan_is_byte_deterministic -v`

Expected: PASS.

- [ ] **Step 6: Run each validator against generated artifacts**

Run the test helper that invokes both scripts against the generated target.

Expected: both scripts return 0; a mutated enterprise/SQLite manifest returns 1.

- [ ] **Step 7: Commit manifest generation**

```bash
git add schemas scripts/create_agent_from_blueprint.py scripts/validate_experience_manifest.py scripts/validate_memory_manifest.py tests/test_factory_profiles.py
git commit -m "feat(factory): emit experience memory and delivery manifests"
```

### Task 4: Add safe overlay composition

**Files:**
- Modify: `scripts/scaffold_agent_project.py`
- Modify: `scripts/create_agent_from_blueprint.py`
- Create: `templates/browser-react-fastapi/overlay-manifest.json`
- Create: `templates/browser-react-fastapi/README.overlay.md`
- Modify: `tests/test_factory_profiles.py`

**Interfaces:**
- Produces: `scaffold_project(..., overlays: tuple[str, ...] = ()) -> list[str]`.
- Overlay source path: `templates/<overlay>/`.
- Overlay manifest maps explicit `source` paths to explicit project-relative `destination` paths.

- [ ] **Step 1: Write failing dry-run and non-overwrite tests**

Assert `overlays=("browser-react-fastapi",)` maps `README.overlay.md` to `docs/browser-experience.md` in dry-run, leaves the target absent, and rejects duplicate destination paths whose bytes differ.

- [ ] **Step 2: Verify RED**

Run: `python -m unittest tests.test_factory_profiles.FactoryProfileTests.test_scaffold_composes_overlay_without_mutating_dry_run -v`

Expected: FAIL because `overlays` is unsupported.

- [ ] **Step 3: Implement deterministic overlay collection**

Resolve overlay names against `SKILL_ROOT/templates`, reject path separators and unknown names, validate each manifest entry, resolve source and destination paths without escape, merge sorted destination paths, allow identical duplicate bytes only, and retain the existing empty-target guard.

- [ ] **Step 4: Verify GREEN**

Run the focused overlay tests and the existing Python/TypeScript/generic scaffold tests.

Expected: PASS.

- [ ] **Step 5: Commit overlay composition**

```bash
git add scripts/scaffold_agent_project.py scripts/create_agent_from_blueprint.py templates/browser-react-fastapi tests/test_factory_profiles.py
git commit -m "feat(scaffold): compose optional governed overlays"
```

### Task 5: Add examples, routing, and package validation

**Files:**
- Create: `examples/browser-enterprise-agent-blueprint.json`
- Create: `examples/local-memory-agent-blueprint.json`
- Create: `references/browser-experience.md`
- Create: `references/memory-deployment.md`
- Create: `assets/browser-control-plane.mmd`
- Create: `assets/memory-platform.mmd`
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `references/workflow.md`
- Modify: `references/architecture.md`
- Modify: `references/agent-factory.md`
- Modify: `references/memory-system.md`
- Modify: `references/testing-and-evaluation.md`
- Modify: `references/production-checklist.md`
- Modify: `scripts/validate_skill_structure.py`
- Modify: `tests/test_scripts.py`

**Interfaces:**
- Produces progressive-disclosure routes from `SKILL.md`.
- Produces valid examples with no inline credentials.

- [ ] **Step 1: Write a failing structure/resource test**

Assert every new reference, schema, asset, script, and example is listed in the structure validator and both examples produce non-blocked deterministic plans.

- [ ] **Step 2: Verify RED**

Run the focused resource test.

Expected: FAIL on missing resources.

- [ ] **Step 3: Add resources and routing text**

Document the exact profiles, non-install boundary, UI safe projection, Memory decision tree, and deployment engagement. Keep `SKILL.md` concise and route detail to the two new references.

- [ ] **Step 4: Verify GREEN**

Run: `python scripts/validate_skill_structure.py --skill . --json`

Expected: exit 0 with `status: passed`.

- [ ] **Step 5: Run the full Skill suite**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass with zero failures.

- [ ] **Step 6: Inspect the diff and commit the foundation**

Run: `git diff --check && git status --short`

Then:

```bash
git add SKILL.md README.md references assets examples scripts/validate_skill_structure.py tests/test_scripts.py
git commit -m "docs: route browser experience and memory platform profiles"
```
