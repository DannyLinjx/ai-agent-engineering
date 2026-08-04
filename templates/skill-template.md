---
name: example-agent-skill
description: Use when the agent must follow the example domain workflow and produce its defined evidence.
---

# Example agent skill

## Workflow

1. Inspect inputs and constraints.
2. Select the smallest relevant references and tools.
3. Execute under permissions and budgets.
4. Verify the completion criteria.
5. Return evidence, limitations, and next actions.

## Resources

- Read `references/domain-rules.md` for domain decisions.
- Run `scripts/validate_output.py` before claiming completion.
- Copy `assets/output-template.md` for the deliverable.
