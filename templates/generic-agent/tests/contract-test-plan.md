# {{PROJECT_NAME}} Contract Test Plan

- Validate configuration and state against the copied JSON Schemas.
- Round-trip state through the repository's native serializer.
- Cover bounded-loop completion, failure, cancellation, timeout, and budget exhaustion.
- Cover permission `ALLOW`, `DENY`, and paused `ASK` behavior.
- Verify workspace, tenant, credential, artifact, and cache isolation.
- Mark unselected optional integrations `skipped` or `not_applicable`.
