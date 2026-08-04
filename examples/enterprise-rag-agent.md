# Enterprise RAG agent: configuration validation

## Goal

Determine whether a product configuration is legal using enterprise product, relationship, and rule data, then explain why with evidence.

## Architecture

Intent parser normalizes product/config IDs. A structured product tool fetches attributes; a relationship tool fetches compatibility edges; a versioned rule skill evaluates constraints. The agent never substitutes vector similarity for authoritative structured rules.

## Workflow

1. authenticate tenant/user and resolve product/version/effective date;
2. identify missing inputs and request them;
3. retrieve scoped product records and relationship edges;
4. load only the matching rule skill/version;
5. compute a deterministic rule result;
6. verify evidence completeness and data freshness;
7. return valid/invalid/indeterminate, reasons, source record IDs, rule version, and remediation.

## Safety and isolation

Repository queries require tenant predicates at the repository boundary. Result caches include tenant, product version, and rule version. Credentials are short-lived references. Logs contain record IDs and hashes, not confidential payloads. Cross-tenant direct-ID and search leakage are critical test cases.

## Failure mode

Missing or conflicting authoritative data yields `indeterminate`; the agent does not invent compatibility. Provider/search outage uses structured data fallback if authorized or returns a clear blocked result.
