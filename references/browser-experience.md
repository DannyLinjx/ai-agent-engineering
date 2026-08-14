# Browser experience

Use a Browser Experience when users need conversation, Run inspection, approvals,
artifacts, Memory, or operations without a terminal. The Browser is a governed
projection of server-owned Agent state; it is not the Agent runtime.

## Profiles

| Profile | Required surfaces | Intended use |
|---|---|---|
| `headless` | none | API, CLI, scheduled, or embedded Agent |
| `browser_chat` | conversation, Run inspector, approvals, artifacts, Memory | focused end-user workflow |
| `operations_console` | browser chat plus overview, Runs, audit, models, capabilities, settings, access, health | enterprise operation and governance |

The first runnable reference stack is `react_fastapi`: React/Vite generates static
assets and FastAPI owns authentication, API contracts, durable commands, and safe
event projection. Frontend build tools are not required in the production Python
runtime after assets are built.

The reference UI uses an industrial control-ledger visual language: dense evidence
where operators need it, generous working space around the current task, explicit
connection/security state, keyboard-visible focus, reduced-motion support, and a
desktop three-pane workspace that collapses to linear tablet/mobile flow. Routes are
registered only from the Experience Manifest and administrator surfaces remain
role-filtered.

## Control-plane boundary

Follow `assets/browser-control-plane.mmd`:

- API handlers validate, authorize, persist commands, and return projections; they
  never run Agent tools or resolve model credentials.
- A separately invoked Worker leases durable Jobs, runs the bounded Agent runtime,
  and writes allowlisted Run Events.
- SSE is a cursor-addressable projection (`after=<sequence>`), supports replay after
  reconnect, and authorizes the subscription before reading any event.
- The browser receives summaries, status, evidence, tool receipts, and approval facts.
  It never receives hidden reasoning, raw credentials, environment variables,
  unrestricted tool output, or absolute system paths.

## Interaction contract

The primary flow is:

```text
login → create/open conversation → send idempotent command → observe Run timeline
→ decide scoped approval when requested → inspect artifacts/Memory → verified result
```

Use server-side sessions, HttpOnly/SameSite cookies, CSRF protection on unsafe
methods, generic authentication failures, and server-side logout. Every repository
method takes an immutable principal containing tenant, user, role, and session.
Unauthorized object access returns a non-enumerating response.

Approvals bind actor, principal scope, Run, tool/version, normalized parameters,
target, risk, evidence, expiry, and action fingerprint. Any material change requires
new approval. Artifacts use authorized opaque IDs and safe download headers; do not
expose storage paths.

## Factory behavior

Set `experience.profile`, `reference_stack`, `auth`, `realtime`, and `surfaces` in
the Agent Blueprint. The Factory derives capabilities, validates conflicts, writes
`factory/experience-manifest.json`, and composes the selected overlay only for a
supported scaffold. It does not install packages, start services, open a browser,
configure credentials, or deploy.

Validate the generated manifest with:

```bash
python scripts/validate_experience_manifest.py \
  --manifest <agent>/factory/experience-manifest.json --json
```

Use `examples/local-memory-agent-blueprint.json` for browser chat and
`examples/browser-enterprise-agent-blueprint.json` for an operations console.

After explicitly installing the generated candidate's selected dependencies, verify
and package existing build output with:

```bash
pnpm --dir <agent>/web test
pnpm --dir <agent>/web typecheck
pnpm --dir <agent>/web build
pnpm --dir <agent>/web e2e
python <agent>/scripts/build_browser_assets.py \
  --source <agent>/web/dist \
  --destination <agent>/src/agent_control/static_assets
```

The sync script downloads nothing, requires a complete index/JavaScript/CSS build,
accepts only declared static asset types, rejects source/destination nesting and
non-empty destinations, records hashes, and never copies symlinks.

## Verification

At minimum test login/logout, CSRF, cross-tenant object guesses, idempotent command
creation, worker lease recovery, cancellation, SSE replay, approval reject/expire/
parameter change, artifact traversal/type/size, Memory scope, redaction, responsive
keyboard navigation, disconnect/reconnect, and verifier-owned completion. Offline
core tests may leave dependency-backed browser tests `not_applicable`; a selected
Browser profile cannot claim readiness until its backend, frontend, and E2E gates run.
