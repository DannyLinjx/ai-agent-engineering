# Troubleshooting playbook

## Infinite or repetitive tool loop

Inspect normalized action fingerprints, progress signals, plan changes, tool errors, and budgets. Add deterministic repeat/no-progress termination; do not rely on a stronger prompt. Verify a repeated-call scenario.

## Tool succeeds but agent ignores it

Check output schema, truncation/artifact summary, observation insertion, context budget, provenance, and plan-step evidence mapping. Ensure the tool result is not silently dropped during compaction.

## Context overflow or quality decay

Measure each context section, reserve output margin, offload large results, compress observations, summarize sessions, and retrieve fewer skills/memories. Test retention of objective, constraints, approvals, and unmet criteria.

## Unsafe action bypasses approval

Trace every executor entry point. Ensure risk classification uses actual parameters, hard deny precedes allow, approval receipts bind normalized action, and hooks/MCP/subagents call the same permission engine. Add a negative end-to-end test.

## Cannot resume after crash

Check atomic checkpoint/event writes, schema/config fingerprint compatibility, artifact durability, leases, and in-flight side-effect reconciliation. Do not blindly retry non-idempotent tools.

## Memory is irrelevant or leaks

Verify authorization filtering before ranking, scope keys, consent/write policy, conflict handling, retrieval limits, and cache isolation. Rebuild derived indexes after deletion or schema change.

## Model routing is unstable or costly

Separate hard constraints from scoring, pin profile versions, record routing reasons, enforce total budgets, and test outage/fallback. Avoid routing based on unvalidated model self-description.

## Eval passes but production fails

Check scenario coverage, fixture realism, evaluator leakage, model/provider/config drift, tool availability, and trace segmentation. Add the production failure as a versioned regression case after removing sensitive data.

## Debug evidence order

Reproduce → capture state/trace/config fingerprints → localize the failing boundary → form one falsifiable hypothesis → make the smallest authorized change → run focused then regression tests → inspect trace/diff → document cause and residual risk.
