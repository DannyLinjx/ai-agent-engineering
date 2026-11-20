# Controlled Agent Factory

Use the Factory when the requested outcome is to create a new enterprise Agent from requirements or to reproduce a family of Agents from governed specifications. Use normal BUILD/REFACTOR when changing one known codebase without a reusable Blueprint.

## Control-plane rule

The Factory is build-time control plane; the generated Agent Runtime is the execution plane. The creator agent may propose and generate. Deterministic code validates contracts, classifies capability gaps, writes files, runs gates, and records evidence. Humans approve production release, sensitive data access, and high-risk permissions.

## Workflow

1. Normalize objective, users, workflow, deliverables, perception inputs, data, autonomy, service targets, implementation constraints, and acceptance criteria.
2. Resolve material unknowns. Assume only low-risk reversible gaps and record them.
3. Create `agent-blueprint.json` from `schemas/agent-blueprint.schema.json`.
   Normalize Experience, Memory, and Delivery profiles; absent sections use the safe
   backward-compatible defaults documented in `client-experience.md` and
   `memory-deployment.md`.
4. Generate a deterministic Build Recipe with `--plan`; do not mutate the target.
5. Review required, planned, blocked, and not-applicable capabilities plus human approvals.
6. Use `--apply` only when blockers are empty and the target is absent or empty.
7. Implement planned adapters and business capabilities through existing interfaces and the user's phases; P0–P10 is only a fallback dependency ordering.
8. Run contract, architecture, safety, scenario, eval, cost, and readiness gates.
9. Produce an Evidence Bundle and wait for human release approval.

```bash
python scripts/create_agent_from_blueprint.py \
  --blueprint examples/enterprise-agent-blueprint.json \
  --target ./service-agent \
  --plan ./build-recipe.json

python scripts/create_agent_from_blueprint.py \
  --blueprint examples/enterprise-agent-blueprint.json \
  --target ./service-agent \
  --apply \
  --report ./creation-report.json
```

## Clarification threshold

- Continue with an explicit assumption for a low-risk, reversible choice that does not change architecture, data handling, authority, cost ceiling, or acceptance.
- Return `blocked` for unresolved high/critical risk, missing authority, sensitive-data governance, irreversible effects, production ownership, or an unknown required capability.
- Never ask again for information already present in the repository or Blueprint.

## Factory artifacts

| Artifact | Meaning |
|---|---|
| `factory/agent-blueprint.json` | authoritative requested Agent contract |
| `factory/build-recipe.json` | deterministic selection, gaps, phases, approvals, and validation commands |
| `factory/capability-matrix.json` | required/optional capability state and evidence mapping |
| `factory/assembly-manifest.json` | perception, tool, Skill, knowledge, memory, model, Channel, MCP, and instruction plan |
| `factory/experience-manifest.json` | Selected headless/browser/native profile, supported/generated/planned surfaces, safe events and projection boundaries |
| `factory/memory-manifest.json` | canonical store, derived adapters, consent/retention, lifecycle, and ranking boundary |
| `factory/deployment-plan.json` | non-mutating dependency, approval, migration, cutover, rollback, and validation plan |
| `factory/release-checklist.json` | pending automated gates and required human decisions |

Statuses are `planned`, `generated`, `candidate_passed`, `candidate_failed`, `blocked`, and `awaiting_human_approval`. None means deployed.

`delivery.engagement` is descriptive scope, not authorization. Even `end_to_end`
leaves `installation_allowed` and `deployment_allowed` false until a later task has
explicit authority and passes the recorded approval gates.

## Perception and reflection

Normalize intent, entities, text, files, image/OCR, history, and external events into typed, provenance-carrying inputs. Declaring a modality does not prove its adapter exists; mark missing adapters planned or blocked.

Map the iterative loop as:

```text
typed input → scoped context → typed model decision → authorized tool
→ validated result/evidence → verifier → evidence-triggered replan or completion
```

Model reflection may propose a repair. It cannot approve its own work or replace the verifier.

## Instruction lifecycle

Generated instructions record source, version/fingerprint, tests, and review state. A creator agent may propose a prompt change as a candidate artifact. It must not change immutable safety instructions, permissions, tenant scope, or production policy without review and approval.

## Prohibitions

- Do not embed credentials or request raw secrets.
- Do not fabricate OCR, retrieval, tools, live providers, or external adapters from a Blueprint declaration.
- Do not make vector databases, queues, caches, MCP, multiple agents, or a vendor framework mandatory.
- Do not overwrite non-empty targets.
- Do not install dependencies, push, publish, or deploy from the Factory script.
- Do not report production readiness from generated templates or model self-review.

## Common mistakes

| Mistake | Correct behavior |
|---|---|
| Treating the source diagram as a mandatory technology stack | Select technologies from Blueprint constraints and capability evidence |
| Building every P0–P10 module immediately | Generate the smallest secure closed loop and mark optional modules not applicable |
| Calling `--apply` before reviewing the recipe | Run `--plan`, resolve blockers, then apply |
| Treating `awaiting_human_approval` as released | Complete automated gates and obtain the named human decisions |
| Using free-form ReAct as the control plane | Keep typed decisions, deterministic permissions, and verifier-owned completion |

## Honest support boundaries

A `native_chat`/`native_cli` experience with `stdio` or `local_ipc` plans an existing Harness client; the current generator does not implement a native GUI. It may generate the selected core scaffold with native surfaces explicitly planned, never inject a React/HTTP overlay to satisfy the selection.

Local `encrypted_files` and `scoped_markdown` memory selections preserve/plans the existing canonical authority and require adapter work; no file-memory persistence implementation or database migration is generated. Existing SQLite/PostgreSQL profiles retain their behavior.

`max_steps=0` expresses an explicitly uncapped step count in a Blueprint, not missing safeguards. Planning retains positive deadline/token and progress/cancel requirements. The reference execution scaffold does not implement all those guards, so apply rejects this setting before any target write instead of generating an unbounded or zero-iteration loop. Integrate a governed Runtime before claiming executable support.

Use [native-local-agent-blueprint.json](../examples/native-local-agent-blueprint.json) for an independently synthetic native/stdio and planned encrypted-file selection. It is a planning/core scaffold example, not a generated desktop application or installed storage backend.
