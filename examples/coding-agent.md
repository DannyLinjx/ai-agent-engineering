# Coding agent: complete vertical slice

## Goal

Given “inspect the current project, fix failing tests, and explain why,” safely modify an authorized workspace and produce verified evidence.

## Capability design

- Interface: CLI/IDE with user, session, workspace, and cancellation.
- Planner: inspect → reproduce → diagnose → patch → focused test → regression test → diff review → report.
- Tools: list/search/read, test command, apply patch, git status/diff. No push/deploy.
- Permissions: workspace reads allowed; writes ask or follow session grant; commands allowlisted; secrets and workspace escape denied.
- Context: keep failure excerpt and code slices; offload full logs.
- Session/checkpoint: after reproduction and each verified patch.
- Verifier: failing test first, then passing focused/regression suite, diff contains intended files only.

## Plan and evidence

| Step | Action | Completion | Evidence |
|---|---|---|---|
| 1 | inspect instructions/manifests/tree | constraints known | manifest artifact |
| 2 | run smallest failing command | failure reproduced | command/exit/log hash |
| 3 | localize cause | falsifiable explanation | linked file/trace |
| 4 | apply minimal patch | intended behavior changed | patch receipt |
| 5 | verify | focused and relevant regression pass | test report |
| 6 | review | no secret/unrelated/destructive diff | diff summary |

## Negative cases

Reject attempts to read `.env`, execute a broad destructive command, alter tests merely to hide the failure, claim success without rerunning, or push without separate authorization.

## Acceptance assertion

The final result names cause, changed files, commands and exit codes, remaining limitations, and artifact paths. A model-generated “tests pass” sentence never satisfies the verifier.
