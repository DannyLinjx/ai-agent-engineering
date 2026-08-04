# Source requirements traceability

This implementation derives from `AI Agent Engineering Skill.docx`. The map shows where its required capabilities are implemented, while adding production controls that make the workflow executable and testable.

| Source requirement | Skill implementation |
|---|---|
| DESIGN/BUILD/REFACTOR/AUDIT/DEBUG/EXTEND/TEST/DOCUMENT | `SKILL.md`, `references/workflow.md` |
| inspect existing project and classify change | workflow steps 1–2; `generate_module_manifest.py` |
| capability matrix and P0–P10 plan | workflow steps 3–4; templates/schema/assets |
| modular architecture and interfaces | `references/architecture.md`; TypeScript/Python scaffolds |
| AgentState, planner, bounded ReAct loop | runtime reference; state/config schemas |
| tool registry and safety envelope | tool reference; tool schema/templates; safety audit |
| skill loader | skill-system reference; skill template |
| context offload and compaction | context reference; runtime acceptance catalog |
| sessions, checkpoint, resume/rewind/cancel | session reference; state schema |
| short/long/profile memory | memory reference |
| ALLOW/DENY/ASK and human approval | permission reference; policy template; diagram |
| lifecycle hooks | hook reference and TypeScript/Python templates |
| bounded subagents | subagent reference/templates/diagram |
| lazy MCP integration | MCP reference; config template |
| model routing and fallback | model-routing reference; config/schema |
| optional user-selected Channel/Provider/MCP | channels/integrations reference; integration schema/template/scripts |
| verification before completion | testing/evaluation reference and acceptance runner |
| execution logs, metrics, audit, cost | observability reference; trace schema |
| multi-user isolation | isolation reference and acceptance cases |
| TypeScript and Python support | `templates/typescript-agent/`, `templates/python-agent/` |
| coding, research, RAG, computer control, multi-agent examples | `examples/` |
| scripts and real structural validation | `scripts/`; `tests/test_scripts.py` |
| final production gate | production checklist and readiness schema |

Additional safeguards include threat modeling, immutable identity propagation, configuration/version provenance, idempotency and crash reconciliation, prompt-injection controls, online/offline eval separation, SLOs, canary rollout, rollback, incident response, and cost regression gates.
