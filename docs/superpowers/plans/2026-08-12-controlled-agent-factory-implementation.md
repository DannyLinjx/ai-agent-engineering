# Controlled Agent Factory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic build-time Agent Factory that converts a validated enterprise Agent Blueprint into a reproducible candidate project and evidence artifacts while preserving human approval for release.

**Architecture:** Keep the existing runtime and P0–P10 execution plane unchanged. Add one JSON Blueprint contract, one standard-library plan/apply generator that reuses `scaffold_agent_project.py`, and progressive-disclosure documentation and gates that map factory artifacts into the existing capability, safety, test, and production workflow.

**Tech Stack:** Python 3.10+ standard library, JSON/JSON Schema Draft 2020-12 contracts, Markdown, Mermaid, YAML assets, and `unittest` regression tests.

## Global Constraints

- Do not modify existing runtime, planner, permission, memory, context, tool execution, model routing, or checkpoint implementations.
- Do not add runtime dependencies; Skill scripts remain Python standard-library only.
- Do not install dependencies, acquire credentials, contact live providers, commit/push generated projects, or deploy.
- Keep Channels and MCP optional and development/test models defaulted to `mock`.
- Treat production targets, sensitive data, external writes, high-risk tools, and scope expansion as human-approval requirements.
- A generated candidate may end only in `candidate_failed` or `awaiting_human_approval`; no automated status means deployed or production-approved.
- Reuse existing Python, TypeScript, and generic scaffolds instead of creating a second runtime template.
- Make Build Recipes deterministic: no timestamps, random IDs, absolute target paths, or other volatile fields in recipe content.

---

### Task 1: Blueprint Contract and Examples

**Files:**
- Create: `schemas/agent-blueprint.schema.json`
- Create: `templates/agent-blueprint.json`
- Create: `examples/enterprise-agent-blueprint.json`
- Modify: `tests/test_scripts.py`

**Interfaces:**
- Consumes: capability names from `assets/capability-catalog.json` and existing language/profile choices.
- Produces: Blueprint objects with top-level keys `version`, `blueprint_id`, `agent`, `product`, `perception`, `data_governance`, `capabilities`, `autonomy`, `service`, `implementation`, `verification`, `assumptions`, and `unknowns`.

- [ ] **Step 1: Add a failing contract-shape test**

Add `test_agent_blueprint_contract_and_examples` to `tests/test_scripts.py`. It must assert that the schema, template, and enterprise example exist; both examples contain every required top-level key; the template uses `development` and optional integrations default to `none`/`mock`; the enterprise example declares at least one perception modality, required capability, approval-required action, acceptance criterion, and deterministic assertion; neither example contains keys matching `api_key`, `password`, `secret`, or `token` with inline values.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_blueprint_contract_and_examples -v
```

Expected: FAIL because `schemas/agent-blueprint.schema.json` and example files do not exist.

- [ ] **Step 3: Create the closed Blueprint schema**

Define all governed sections as `additionalProperties: false`. Use:

- language enum: `python`, `typescript`, `generic`;
- profile enum: `development`, `test`, `production`;
- autonomy enum: `assistive`, `supervised`, `bounded_autonomous`;
- modality enum: `text`, `file`, `image`, `ocr`, `history`, `external_event`;
- data class enum: `public`, `internal`, `confidential`, `restricted`;
- unknown risk enum: `low`, `medium`, `high`, `critical`;
- resolution enum: `assumed`, `resolved`, `open`.

Require non-empty objectives, intended users, business workflow, deliverables, acceptance criteria, owner, escalation owner, budgets, verifier type, security gates, and implementation language/profile/deployment environment. Credential fields must not exist in the contract.

- [ ] **Step 4: Create a valid minimal template and enterprise example**

The minimal template must be development-safe: text input, mock model, no Channel/MCP, no sensitive data, supervised autonomy, and explicit acceptance/security criteria. The enterprise example should describe a multi-tenant internal service-operations Agent with text/file/event input, tool and knowledge capabilities, confidential data, approval for external writes, deterministic assertions, and production target.

- [ ] **Step 5: Run the focused test and full JSON parse test**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_blueprint_contract_and_examples tests.test_scripts.SkillScriptTests.test_all_json_files_parse -v
```

Expected: PASS.

---

### Task 2: Deterministic Planning and Semantic Gates

**Files:**
- Create: `scripts/create_agent_from_blueprint.py`
- Modify: `tests/test_scripts.py`

**Interfaces:**
- Consumes: Blueprint JSON, `assets/capability-catalog.json`, and a target path used only to check mutation boundaries.
- Produces: `build-recipe.json` with `version`, `blueprint_id`, `blueprint_hash`, `status`, `scaffold`, `profile`, `applicable_phases`, `capabilities`, `assumptions`, `blockers`, `human_approvals`, `generated_files`, `validation_commands`, and `recipe_hash`.
- Internal functions: `load_blueprint(path: Path) -> dict`, `validate_blueprint(value: dict) -> list[dict]`, `build_recipe(value: dict) -> dict`, `write_recipe(path: Path, recipe: dict) -> None`.

- [ ] **Step 1: Add failing tests for stable planning and blocked planning**

Add:

- `test_agent_factory_plan_is_deterministic_and_non_mutating`: invoke `--plan` twice with the enterprise example, assert byte-identical recipes, `status == "planned"`, target absent, production approval present, recipe hash stable, and all required capabilities classified.
- `test_agent_factory_blocks_material_unknown_without_target_write`: copy the template, append an open `high` unknown, invoke `--plan` expecting exit 1, assert `status == "blocked"`, blocker code `material-unknown`, and target absent.

- [ ] **Step 2: Run both tests and verify RED**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_factory_plan_is_deterministic_and_non_mutating tests.test_scripts.SkillScriptTests.test_agent_factory_blocks_material_unknown_without_target_write -v
```

Expected: FAIL because the generator script does not exist.

- [ ] **Step 3: Implement dependency-free structural and semantic validation**

Validate exact required top-level and section keys, scalar/list types, finite enums, positive budgets, non-empty acceptance/security arrays, capability catalog membership, absence of credential-like keys/values, and unknown resolution. Emit issues through `_common.issue` and `_common.result` conventions.

Block when:

- any structural validation issue exists;
- a required capability is not in the catalog;
- an unknown with `high`/`critical` risk remains `open`;
- production lacks an owner, escalation owner, availability/quality targets, or required release approval;
- irreversible/external-write actions are allowed without appearing in approval-required actions.

- [ ] **Step 4: Implement deterministic recipe construction and CLI**

Use canonical JSON (`sort_keys=True`, compact separators) for content hashes. Sort capabilities, phases, approvals, blockers, and generated-file paths. Derive applicable phases from capability-to-phase rules. Compute `recipe_hash` after omitting `recipe_hash` itself. `--plan PATH` always writes a recipe, including blocked recipes, and returns 1 for blocked/invalid values.

CLI arguments:

```text
--blueprint PATH --target PATH (--plan PATH | --apply) [--report PATH]
```

Make `--plan` and `--apply` mutually exclusive.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run the two tests from Step 2. Expected: PASS.

---

### Task 3: Controlled Apply and Candidate Artifacts

**Files:**
- Modify: `scripts/create_agent_from_blueprint.py`
- Modify: `scripts/scaffold_agent_project.py`
- Modify: `tests/test_scripts.py`

**Interfaces:**
- Consumes: `build_recipe(value)` and reusable `scaffold_project(language: str, name: str, target: Path, dry_run: bool = False) -> list[str]` extracted from the existing scaffold script.
- Produces inside the candidate project:
  - `factory/agent-blueprint.json`
  - `factory/build-recipe.json`
  - `factory/capability-matrix.json`
  - `factory/assembly-manifest.json`
  - `factory/release-checklist.json`
  - report JSON at `--report` when supplied.

- [ ] **Step 1: Add failing apply tests**

Add:

- `test_agent_factory_apply_generates_candidate_artifacts`: apply the enterprise Blueprint to a temporary Python project, assert runtime scaffold exists, all five factory artifacts exist, status is `awaiting_human_approval`, no deployment action exists, optional integrations follow Blueprint selection, and required capabilities map to `implemented`, `planned`, or `blocked` with evidence paths.
- `test_agent_factory_apply_supports_generic_scaffold`: apply a modified development Blueprint using `generic`, assert schema/module-plan files exist and no `src` directory exists.
- `test_agent_factory_rejects_non_empty_target_without_mutation`: create sentinel file, expect exit 2, and assert sentinel content and directory listing remain unchanged.

- [ ] **Step 2: Run the apply tests and verify RED**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_factory_apply_generates_candidate_artifacts tests.test_scripts.SkillScriptTests.test_agent_factory_apply_supports_generic_scaffold tests.test_scripts.SkillScriptTests.test_agent_factory_rejects_non_empty_target_without_mutation -v
```

Expected: FAIL because apply is not implemented and scaffold logic is not reusable.

- [ ] **Step 3: Extract the existing scaffold behavior into `scaffold_project`**

Preserve current CLI output and tests. The function must validate available language, reject non-empty targets, apply existing replacements, copy shared files and generic schemas, create directory markers, and return the sorted generated relative paths.

- [ ] **Step 4: Implement apply and artifact rendering**

`--apply` must:

1. validate and build the recipe;
2. refuse blocked recipes without creating the target;
3. reject a non-empty target before any write;
4. scaffold the selected language;
5. copy the canonical Blueprint and recipe;
6. derive capability matrix records with explicit state, phase, files, verification, and evidence;
7. derive an assembly manifest for perception, tools, Skills, knowledge, memory, model, Channel, MCP, and subagents;
8. derive a release checklist whose automated gate results are `pending` and whose decision is `awaiting_human_approval`;
9. write a report with candidate status and relative artifact paths.

The report may contain the resolved target path; the deterministic recipe must not.

- [ ] **Step 5: Run apply tests and all scaffold tests**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_factory_apply_generates_candidate_artifacts tests.test_scripts.SkillScriptTests.test_agent_factory_apply_supports_generic_scaffold tests.test_scripts.SkillScriptTests.test_agent_factory_rejects_non_empty_target_without_mutation tests.test_scripts.SkillScriptTests.test_python_scaffold_and_acceptance tests.test_scripts.SkillScriptTests.test_typescript_scaffold_dry_run tests.test_scripts.SkillScriptTests.test_generic_scaffold_is_language_neutral -v
```

Expected: PASS.

---

### Task 4: Agent Factory Reference, Routing, Diagram, and Gates

**Files:**
- Create: `references/agent-factory.md`
- Create: `assets/agent-factory-flow.mmd`
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `assets/capability-catalog.json`
- Modify: `assets/phase-gates.yaml`
- Modify: `evals/evals.json`
- Modify: `scripts/validate_skill_structure.py`
- Modify: `tests/test_scripts.py`

**Interfaces:**
- Consumes: generator CLI and artifact names from Tasks 2–3.
- Produces: discoverable Factory workflow with a required-resource structure gate and a canonical enterprise-Agent evaluation case.

- [ ] **Step 1: Add failing structure and documentation assertions**

Extend `test_structure_validator` or add `test_agent_factory_is_routed_and_gated` to assert:

- structure validation requires the six new resources;
- `SKILL.md` links directly to `references/agent-factory.md` and includes plan/apply commands;
- capability catalog includes `agent-factory` and `perception-input`;
- P0 requires `agent-blueprint` and `build-recipe` evidence;
- P8 requires `factory-evidence-bundle`;
- P10 requires `human-release-approval`;
- evals include `create-enterprise-agent-factory` and expect Blueprint, recipe, candidate evidence, and human release approval.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python -m unittest tests.test_scripts.SkillScriptTests.test_agent_factory_is_routed_and_gated -v
```

Expected: FAIL because routing, reference, diagram, catalog, and gates are absent.

- [ ] **Step 3: Write the progressive-disclosure Factory reference**

Document:

- when to use the Factory versus normal BUILD/REFACTOR;
- input normalization and clarification thresholds;
- Blueprint → gap → recipe → apply → evidence → human approval;
- perception and reflection mappings;
- plan/apply command examples;
- artifact meanings and lifecycle statuses;
- hard prohibitions and common mistakes.

Keep detailed content in `references/agent-factory.md`; add only a concise routing row, invariant paragraph, and command examples to `SKILL.md`.

- [ ] **Step 4: Add diagram, catalog entries, phase evidence, README, and eval**

Keep existing P0–P10 numbering. Add factory evidence to existing phases. Update README quick start, directory tree, script table, reference navigation, and test coverage. Do not claim automatic deployment or full implementation of optional adapters.

- [ ] **Step 5: Update structure requirements and run focused test**

Add the six created resources to `REQUIRED`. Run the test from Step 2. Expected: PASS.

---

### Task 5: Security Failure Paths and Full Verification

**Files:**
- Modify: `tests/test_scripts.py`
- Modify if required by observed failures: `scripts/create_agent_from_blueprint.py`

**Interfaces:**
- Consumes: finalized Factory CLI.
- Produces: regression evidence for credential rejection, approval enforcement, non-mutation, deterministic output, and backward compatibility.

- [ ] **Step 1: Add failing negative tests**

Add:

- `test_agent_factory_rejects_inline_credentials_before_write`: inject `api_key: raw-secret-value`, expect exit 1, issue `inline-credential`, no target.
- `test_agent_factory_requires_approval_for_external_write`: remove an external-write action from `approval_required_actions`, expect blocked recipe with `approval-required`, no target.
- `test_agent_factory_required_capability_must_be_catalogued`: add an unknown required capability, expect `unknown-capability`, no target.

- [ ] **Step 2: Run negative tests and verify RED if any behavior is absent**

Run the three tests. Expected: at least one FAIL until all semantic gates are implemented.

- [ ] **Step 3: Implement only missing gate behavior**

Do not broaden the contract. Add the minimal semantic checks needed for the named issue codes and no-write guarantees.

- [ ] **Step 4: Run complete test and validation suite**

Run:

```bash
python scripts/validate_skill_structure.py --skill . --json
python -m unittest discover -s tests -v
git diff --check
```

Expected: structure `passed`, all tests `OK`, and no whitespace errors.

- [ ] **Step 5: Run manual Factory smoke checks**

In a temporary directory:

```bash
python scripts/create_agent_from_blueprint.py --blueprint examples/enterprise-agent-blueprint.json --target <tmp>/enterprise-agent --plan <tmp>/recipe.json
python scripts/create_agent_from_blueprint.py --blueprint examples/enterprise-agent-blueprint.json --target <tmp>/enterprise-agent --apply --report <tmp>/report.json
python scripts/validate_agent_architecture.py --project <tmp>/enterprise-agent --json
python scripts/audit_agent_safety.py --project <tmp>/enterprise-agent --json
```

Expected: stable planned recipe, candidate generated, report status `awaiting_human_approval`, architecture and safety checks pass or report only evidence-qualified warnings, and no deployment side effects.

- [ ] **Step 6: Review final diff against the design constraints**

Confirm only the agreed Factory files plus documentation/tests changed; no runtime implementation file changed; no credentials, caches, archives, build outputs, or generated candidate projects are tracked.
