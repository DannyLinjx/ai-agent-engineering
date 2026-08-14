# Browser Reference Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runnable React/Vite + FastAPI browser overlay that gives generated Python Agents complete conversation, Run observation, approval, artifact, Memory, and optional operations-console interaction.

**Architecture:** Serve a same-origin browser application from a FastAPI control plane. Persist browser commands and safe Run Events, execute Agent work outside request handlers through a Worker boundary, and stream durable projections over cursor-addressable SSE. Package built frontend assets into the Python candidate while keeping Node.js out of the production runtime.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic, Uvicorn, React, TypeScript, Vite, React Router, TanStack Query, Zod, Vitest, Testing Library, MSW, Playwright.

## Global Constraints

- Modify only `/Users/danny/Documents/skills/ai-agent-engineering`.
- The Browser overlay is generated only when selected; headless scaffolds remain unchanged.
- API request handlers never run Agent tools or resolve model credentials.
- Browser Events use the safe allowlist and never expose hidden reasoning, raw secrets, environment variables, unrestricted output, or absolute system paths.
- Core Skill tests remain offline; dependency-backed browser build/E2E is a separate selected-profile gate.
- Factory generation never runs npm/pip installation, opens a browser, starts a service, or deploys.

---

## File map

- `templates/browser-react-fastapi/backend/agent_control/`: FastAPI app, auth, persistence, Runs, Events, approvals, artifacts, Memory projections, static serving.
- `templates/browser-react-fastapi/backend/tests/`: backend contract, security, and recovery tests.
- `templates/browser-react-fastapi/web/`: React/Vite application and browser tests.
- `templates/browser-react-fastapi/overlay-manifest.json`: deterministic overlay metadata and destination mapping.
- `tests/test_browser_overlay.py`: Skill-level generation and no-install tests.
- `examples/acceptance-commands-browser.json`: selected-profile verification commands.
- `references/browser-experience.md`: operator/developer contract.

### Task 1: Establish overlay package and safe browser event contract

**Files:**
- Modify: `templates/browser-react-fastapi/overlay-manifest.json`
- Create: `templates/browser-react-fastapi/backend/agent_control/events.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_events.py`
- Create: `tests/test_browser_overlay.py`
- Modify: `scripts/create_agent_from_blueprint.py`

**Interfaces:**
- Produces: `BrowserRunEvent` and `safe_event(event_type, payload, scope, sequence)`.
- Overlay destination: backend files merge into `src/agent_control`, frontend files merge into `web`.

- [ ] **Step 1: Write failing safe-event tests**

Assert allowed events preserve safe fields, secret/path/reasoning keys are removed, output previews are bounded, and unknown event types raise `ValueError`.

- [ ] **Step 2: Verify RED**

Run generated backend event tests with `PYTHONPATH=src`.

Expected: import failure because `agent_control.events` is absent.

- [ ] **Step 3: Implement immutable event projection**

Use the exact event allowlist from `schemas/browser-run-event.schema.json`. Event fields are `id`, `run_id`, `sequence`, `type`, `timestamp`, `status`, and sanitized `payload`. Redaction is recursive and caps strings and arrays.

- [ ] **Step 4: Verify GREEN**

Run focused event tests.

Expected: PASS.

- [ ] **Step 5: Verify profile generation without installation**

Scaffold a browser Blueprint and assert `web/package.json` and backend files exist while `web/node_modules`, `.venv`, `.env`, and running service files do not.

- [ ] **Step 6: Commit the browser contract slice**

```bash
git add templates/browser-react-fastapi scripts/create_agent_from_blueprint.py tests/test_browser_overlay.py
git commit -m "feat(browser): add governed overlay and safe events"
```

### Task 2: Implement authentication and scoped persistence

**Files:**
- Create: `templates/browser-react-fastapi/backend/agent_control/config.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/db.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/models.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/auth.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/api.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_auth.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_scope.py`

**Interfaces:**
- Produces: immutable `Principal(tenant_id, user_id, role, session_id)`.
- Produces routes: login, logout, and current user.
- Uses server-side session token hashes and per-session CSRF hashes.

- [ ] **Step 1: Write failing authentication tests**

Cover successful login, generic failure, server-side logout, CSRF rejection on unsafe methods, HttpOnly/SameSite cookie, and no credential values in responses.

- [ ] **Step 2: Verify RED**

Expected: route imports fail.

- [ ] **Step 3: Implement settings, SQLite engine, migrations, and local account auth**

Use loopback-safe defaults. Persist only password hashes and token/CSRF hashes. Production config rejects `auth=none` and non-loopback plain HTTP.

- [ ] **Step 4: Write and verify failing scope tests**

Create Alice and Bob with similarly shaped IDs. Assert Bob receives 404 for Alice's object and no list/search endpoint returns it.

- [ ] **Step 5: Implement mandatory scoped repository predicates**

Repositories require Principal rather than optional tenant/user arguments. Background commands persist immutable scope fields.

- [ ] **Step 6: Verify GREEN and commit**

Run backend auth/scope tests, then:

```bash
git add templates/browser-react-fastapi/backend
git commit -m "feat(browser): add authenticated scoped control plane"
```

### Task 3: Add durable conversations, Runs, Jobs, and SSE

**Files:**
- Create: `templates/browser-react-fastapi/backend/agent_control/conversations.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/runs.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/worker.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/sse.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_runs.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_sse.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_worker.py`

**Interfaces:**
- `send_message(principal, conversation_id, text, idempotency_key, profile) -> RunProjection`.
- Worker lease methods: `lease_next`, `heartbeat`, `complete`, `fail`, `release`.
- SSE: `GET /api/v1/runs/{run_id}/events?after=<sequence>`.

- [ ] **Step 1: Write failing transaction/idempotency tests**

Assert one request creates Message, Run, and Job atomically; retry with the same key returns the same Run; a different user cannot reuse the key to observe it.

- [ ] **Step 2: Verify RED and implement the minimal repository transaction**

Expected initial failure: route/repository missing. Implement only transaction and projection needed by the test.

- [ ] **Step 3: Write failing Worker lease/cancellation tests**

Assert one owner leases a Job, stale owners cannot complete it, cancellation is durable, and Worker checks cancellation between steps.

- [ ] **Step 4: Implement bounded Worker adapter**

The reference Worker accepts an injected Agent execution function. The API never calls it. Persist safe Events through the event projector.

- [ ] **Step 5: Write failing SSE replay tests**

Assert replay after sequence 2 returns 3+, duplicate IDs are impossible, heartbeat is emitted when idle, and unauthorized subscriptions return 404.

- [ ] **Step 6: Implement cursor replay and verify GREEN**

Run Runs, Worker, and SSE tests.

Expected: PASS.

- [ ] **Step 7: Commit durable interaction**

```bash
git add templates/browser-react-fastapi/backend
git commit -m "feat(browser): add durable runs worker and sse"
```

### Task 4: Add approvals, artifacts, and Memory projections

**Files:**
- Create: `templates/browser-react-fastapi/backend/agent_control/approvals.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/artifacts.py`
- Create: `templates/browser-react-fastapi/backend/agent_control/memory_api.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_approvals.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_artifacts.py`
- Create: `templates/browser-react-fastapi/backend/tests/test_memory_api.py`

**Interfaces:**
- Approval stores exact action fingerprint, parameters, evidence refs, expiry, actor, and decision.
- Artifact API stores bounded metadata and authorizes every download.
- Memory API delegates to the generated MemoryPort and exposes safe summaries/lifecycle.

- [ ] **Step 1: Write failing approval replay tests**

Assert rejection never creates an execution Job, changed parameters invalidate approval, expired approval cannot resume, and approved resume reconstructs the original Principal.

- [ ] **Step 2: Implement immutable approvals and verify GREEN**

Persist decision facts and create Resume Jobs only after exact comparison.

- [ ] **Step 3: Write failing artifact security tests**

Cover allowed type/size, denied shell/HTML upload, quota, path traversal, guessed ID, and safe Content-Disposition.

- [ ] **Step 4: Implement authorized content-addressed artifacts**

Never expose real paths. Write metadata and object atomically or reconcile orphaned objects.

- [ ] **Step 5: Write failing Memory API tests**

Assert list/detail/correct/delete/export are scoped, soft deletion removes active recall, and raw internal state is not projected.

- [ ] **Step 6: Implement Memory facade and run all backend tests**

Expected: PASS.

- [ ] **Step 7: Commit governance APIs**

```bash
git add templates/browser-react-fastapi/backend
git commit -m "feat(browser): add approvals artifacts and memory governance"
```

### Task 5: Build the React application shell and API contracts

**Files:**
- Create: `templates/browser-react-fastapi/web/package.json`
- Create: `templates/browser-react-fastapi/web/tsconfig.json`
- Create: `templates/browser-react-fastapi/web/vite.config.ts`
- Create: `templates/browser-react-fastapi/web/src/app/api/client.ts`
- Create: `templates/browser-react-fastapi/web/src/app/router.tsx`
- Create: `templates/browser-react-fastapi/web/src/app/shell/AppShell.tsx`
- Create: `templates/browser-react-fastapi/web/src/app/events/runEventReducer.ts`
- Create: `templates/browser-react-fastapi/web/src/app/events/useRunEvents.ts`
- Create: `templates/browser-react-fastapi/web/src/styles/tokens.css`
- Create: `templates/browser-react-fastapi/web/src/test/`

**Interfaces:**
- `apiRequest(path, schema, init)` validates every response with Zod.
- `useRunEvents(runId)` provides cursor replay, deduplication, gap recovery, and connection state.
- Router is auth-bounded and role-aware.

- [ ] **Step 1: Write failing API and reducer tests**

Cover response-schema rejection, error envelope/correlation ID, CSRF on unsafe methods, duplicate Event ignore, event-gap refetch request, and terminal state projection.

- [ ] **Step 2: Verify RED with Vitest**

Run the exact focused test files after installing pinned dependencies in an approved temporary/generated candidate environment.

Expected: FAIL on missing modules.

- [ ] **Step 3: Implement minimal API client and reducer**

Keep CSRF in memory, use same-origin cookies, and sanitize only on the server; the client still validates the safe contract.

- [ ] **Step 4: Implement AppShell and responsive tokens**

Use semantic navigation, visible connection/security state, focus styles, reduced motion, and role-aware routes.

- [ ] **Step 5: Verify GREEN, typecheck, and commit**

Run unit tests, TypeScript typecheck, and lint. Then:

```bash
git add templates/browser-react-fastapi/web
git commit -m "feat(browser): add typed responsive application shell"
```

### Task 6: Add complete browser-chat surfaces

**Files:**
- Create: `templates/browser-react-fastapi/web/src/features/auth/`
- Create: `templates/browser-react-fastapi/web/src/features/conversations/`
- Create: `templates/browser-react-fastapi/web/src/features/runs/`
- Create: `templates/browser-react-fastapi/web/src/features/approvals/`
- Create: `templates/browser-react-fastapi/web/src/features/artifacts/`
- Create: `templates/browser-react-fastapi/web/src/features/memory/`

**Interfaces:**
- Desktop three-pane workspace; tablet/mobile overlays.
- Composer supports Enter send, Shift+Enter newline, attachment allowlist, Stop, retry, and disabled states.
- Run Inspector renders status, plan, safe tool summaries, evidence, artifacts, costs, and recovery actions.

- [ ] **Step 1: Write failing component workflow tests**

Cover login, create session, send, streaming Event projection, cancel, approval reject/approve, attachment rejection, Memory delete confirmation, loading/empty/error/reconnect states, and keyboard behavior.

- [ ] **Step 2: Verify RED**

Expected: missing page/components.

- [ ] **Step 3: Implement the conversation workspace**

Use TanStack Query for snapshots/mutations and the event reducer for live state. Do not render raw payload JSON.

- [ ] **Step 4: Implement approval, artifact, and Memory surfaces**

Show exact safe action fields, provenance, lifecycle, confidence, expiry, confirmation, and correlation-aware errors.

- [ ] **Step 5: Verify GREEN and commit**

Run frontend unit tests, typecheck, and lint. Then:

```bash
git add templates/browser-react-fastapi/web/src/features
git commit -m "feat(browser): complete governed chat workflow"
```

### Task 7: Add conditional Operations Console surfaces

**Files:**
- Create: `templates/browser-react-fastapi/web/src/features/overview/`
- Create: `templates/browser-react-fastapi/web/src/features/audit/`
- Create: `templates/browser-react-fastapi/web/src/features/models/`
- Create: `templates/browser-react-fastapi/web/src/features/capabilities/`
- Create: `templates/browser-react-fastapi/web/src/features/settings/`
- Modify: `templates/browser-react-fastapi/web/src/app/router.tsx`
- Modify: `templates/browser-react-fastapi/backend/agent_control/api.py`

**Interfaces:**
- Surfaces are registered only when present in Experience Manifest.
- Every card consumes a scoped backend projection; no hard-coded success metrics.

- [ ] **Step 1: Write failing conditional-route tests**

Assert browser-chat profile omits admin routes, operations-console enables selected routes, roles filter Access/Settings, and absent capabilities do not render empty navigation.

- [ ] **Step 2: Verify RED and implement route/capability registry**

Use the generated runtime Experience configuration, not build-time string greps.

- [ ] **Step 3: Write failing data-state tests for every page**

Each page covers loading, empty, error/retry, degraded, and populated states with real response schemas.

- [ ] **Step 4: Implement pages and verify GREEN**

Run all frontend unit tests, typecheck, and lint.

- [ ] **Step 5: Commit operations surfaces**

```bash
git add templates/browser-react-fastapi/web templates/browser-react-fastapi/backend
git commit -m "feat(browser): add conditional operations console"
```

### Task 8: Package, E2E-test, and document the reference candidate

**Files:**
- Create: `templates/browser-react-fastapi/web/playwright.config.ts`
- Create: `templates/browser-react-fastapi/web/e2e/`
- Create: `templates/browser-react-fastapi/backend/agent_control/static.py`
- Create: `templates/browser-react-fastapi/scripts/build_browser_assets.py`
- Create: `examples/acceptance-commands-browser.json`
- Modify: `tests/test_browser_overlay.py`
- Modify: `references/browser-experience.md`
- Modify: `README.md`

**Interfaces:**
- Build script runs test/typecheck/build, verifies index/JS/CSS, and syncs only declared assets.
- Installed Python artifact serves the SPA and API from one origin.

- [ ] **Step 1: Write failing packaged-asset tests**

Assert a generated browser candidate contains build metadata, rejects missing entry/JS/CSS, and serves the built SPA fallback without permitting path traversal.

- [ ] **Step 2: Verify RED and implement the build/sync script**

The script accepts explicit source and destination paths, resolves both, rejects escape, and never downloads dependencies.

- [ ] **Step 3: Add Playwright workflows**

Cover desktop, tablet, and mobile login/chat/Run/reconnect/cancel/approval/Memory/artifact flows; assert no hidden reasoning or unsafe uploaded content appears.

- [ ] **Step 4: Run selected-profile verification**

Run backend tests, frontend tests, typecheck, lint, production build, Playwright, and packaged-asset smoke in a generated temporary candidate. Record any live/provider/service gates as not applicable.

- [ ] **Step 5: Run full Skill regression**

```bash
python -m unittest discover -s tests -v
python scripts/validate_skill_structure.py --skill . --json
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit browser acceptance closure**

```bash
git add templates/browser-react-fastapi examples/acceptance-commands-browser.json tests/test_browser_overlay.py references/browser-experience.md README.md
git commit -m "test(browser): verify packaged responsive reference candidate"
```
