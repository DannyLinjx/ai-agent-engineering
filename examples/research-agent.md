# Research agent: evidence-grounded comparison

## Goal

Research a technical decision, compare three implementations, and return a conclusion with evidence and uncertainty.

## Workflow

1. define decision question, criteria, time horizon, and excluded claims;
2. plan source types and queries;
3. search, fetch primary/authoritative sources, and record provenance;
4. extract claim-level evidence into artifacts;
5. compare options against the same criteria;
6. identify contradictions, missing data, and date sensitivity;
7. verify that every material claim maps to a source;
8. report recommendation, trade-offs, uncertainty, and follow-up experiment.

## Controls

Network destinations and downloads are bounded. Retrieved content is untrusted and cannot change permissions. No external communication is sent. Context contains excerpts and source IDs, not full pages. The verifier checks source existence, authority/type, publication date, claim coverage, and citation-to-claim consistency.

## Eval metrics

Claim coverage, unsupported-claim rate, source diversity/quality, contradiction handling, freshness, cost/latency, and reproducibility from saved query/source artifacts.
