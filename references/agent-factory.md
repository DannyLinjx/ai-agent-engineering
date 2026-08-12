# Controlled Agent Factory

Use the Factory when the requested outcome is to create a new enterprise Agent from requirements or to reproduce a family of Agents from governed specifications. Use normal BUILD/REFACTOR when changing one known codebase without a reusable Blueprint.

## Control-plane rule

The Factory is build-time control plane; the generated Agent Runtime is the execution plane. The creator agent may propose and generate. Deterministic code validates contracts, classifies capability gaps, writes files, runs gates, and records evidence. Humans approve production release, sensitive data access, and high-risk permissions.

## Workflow

1. Normalize objective, users, workflow, deliverables, perception inputs, data, autonomy, service targets, implementation constraints, and acceptance criteria.
2. Resolve material unknowns. Assume only low-risk reversible gaps and record them.
3. Create `agent-blueprint.json` from `schemas/agent-blueprint.schema.json`.
4. Generate a deterministic Build Recipe with `--plan`; do not mutate the target.
5. Review required, planned, blocked, and not-applicable capabilities plus human approvals.
6. Use `--apply` only when blockers are empty and the target is absent or empty.
7. Implement planned adapters and business capabilities through existing interfaces and P0–P10 order.
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
| `factory/release-checklist.json` | pending automated gates and required human decisions |

Statuses are `planned`, `generated`, `candidate_passed`, `candidate_failed`, `blocked`, and `awaiting_human_approval`. None means deployed.

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
