# {{PROJECT_NAME}} Language-Neutral Module Plan

Keep the existing repository language and framework. Map these boundaries to native modules without translating the project to Python or TypeScript:

1. typed contracts and configuration validation;
2. bounded runtime and planner;
3. model, tool, permission, persistence, and verification interfaces;
4. adapters for optional channels, providers, and MCP servers;
5. deterministic tests for control-flow, safety, recovery, and isolation.

Use the copied `schemas/` files as contracts. Record implementation evidence and limitations in the capability matrix before claiming a capability is verified.
