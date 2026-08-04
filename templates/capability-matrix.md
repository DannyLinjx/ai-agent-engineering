# Agent capability matrix

| Capability | Current | Target | Priority | Dependencies | Files/owner | Risk | Verification | Evidence |
|---|---|---|---|---|---|---|---|---|
| Runtime | absent | verified | P1 | P0 contracts | | | bounded-loop scenarios | |
| Planner | absent | verified | P1 | Runtime | | | plan/replan tests | |
| Tools | absent | verified | P2 | Permissions | | | contract and integration tests | |
| Session/checkpoint | absent | verified | P3 | Storage | | | crash recovery | |
| Context | absent | verified | P4 | Artifacts | | | compaction retention | |
| Memory | absent | verified | P5 | Identity/storage | | | lifecycle and isolation | |
| Skills/hooks | absent | verified | P6 | Tools/policy | | | selection and hook tests | |
| Channels | not_applicable | not_applicable | P7 | Identity/runtime | | | selected adapter tests or N/A declaration | |
| Subagents/MCP | absent | verified | P7 | Runtime/tools | | | isolation and fallback | |
| Model Provider | partial | verified | P9 | Model gateway | | | mock core test; live test only when required | |
| Verification/evals | absent | verified | P8 | Scenario fixtures | | | regression report | |
| Model routing | absent | verified | P9 | Model profiles | | | fallback/privacy/budget | |
| Production/observability | absent | verified | P10 | all prior phases | | | readiness gate | |
