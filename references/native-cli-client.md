# Native graphical client over a CLI Harness

Use when the requested desktop client projects an existing CLI/runtime through
stdio or local IPC. A graphical client is not necessarily a terminal emulator,
browser, WebView or HTTP service. Keep the selected native framework and reuse the
existing identity, Runtime, gateways, stores, controls and artifact semantics.
Read [client-experience.md](client-experience.md) for platform-neutral UI contracts.

## Process and transport contract

Map the actual user-clicked launcher → native executable → interpreter/worker →
Harness → Runtime. Specify ownership of each process, startup/handshake, protocol
version, correlation IDs, event sequence, heartbeat/reconnect, shutdown and recovery.
Use fixed argv and reviewed interpreter/source roots. Stdout is the structured
protocol; diagnostics go to stderr. Passwords/tokens must not appear in argv or
unredacted logs. The client cannot choose arbitrary executables or tool commands.

An interactive CLI's loop for the next human input is distinct from the Agent's
governed execution loop. A native client must not implement a second model/tool
controller. A home/workspace lease prevents two Harnesses from owning the same
state. Repeated opening should reuse the product's one intended instance/Harness;
new windows must not silently create independent runtimes.

Startup does not install dependencies or reset private state. Avoid synchronous
long model/Reader/network work before window creation. Diagnose “process running,
no window” using launcher identity, lifecycle, main-thread ownership and observed
system state; do not infer that a missing computer-tool window proves a crash.

## State and native UI

Normalize command acknowledgements and durable Runtime events as in
[session-checkpoint.md](session-checkpoint.md). Disconnect, close-settings, new-chat
and cancel are separate operations. Keep account/session/run/epoch ownership in
every callback; stale work cannot overwrite drafts, uploads, IME or another user's
view. A stopped service or disabled tool is not a transport failure for text chat.

Use native file/save pickers and authorized artifact handlers rather than revealing
internal paths or loading large binaries into the UI. Scope native text-storage
updates so ordinary binding refresh does not reset marked text/caret selection.
Retain keyboard focus without imposing an unwanted mouse-click ring. Dialog focus,
topmost Escape, state retention, themes, scaling and narrow-window layout need
actual native verification in addition to parser/component checks.

## Synchronizing the real launch artifact

For each code iteration affecting delivery, use the repository's actual build/sync
and verification commands. Do not create a new launcher or retain obsolete parallel
entry points unless requested. Preserve one complete working package if a build
fails; stage and validate the replacement before publication. Keep accounts, model
profiles and private runtime state outside bundle replacement.

Record this identity chain:

```text
source/config/prompt → compiled build → packaged artifact/icon/metadata
→ user-clicked entry → mapped native executable → loaded interpreter/modules
→ observed authorized behavior
```

If Python/Harness code changes, normally close and relaunch before checking it;
bringing an old window forward does not reload modules. Test the actual user entry
(Finder, desktop shortcut or OS equivalent), not only a cached binary. Verify cold
open, window and loaded binary/worker, then repeat-open reuse. A cache manifest or
source screenshot cannot establish that a different installed launcher is current.
Only claim the layers actually observed; a successful package check is not GUI E2E.

## OS permissions and bounded verification

System privacy permissions and local-network access may depend on bundle/code
identity. A shell HTTP success does not prove the App has the same permission.
Separate endpoint/protocol failure, process/lifecycle failure, OS authorization,
signature drift, lockscreen and automation-tool access. Use normal authorized OS
flows; do not edit privacy databases, bypass a lockscreen, weaken isolation or
broaden permissions to obtain a green test.

If a physical handoff is required, state the concrete blocker and exact necessary
action. Carry out independent authorized work while waiting. Do not repeat the
same restart/permission/window request without new evidence; retain the unverified
gate and stop after the bounded diagnostic attempt. Do not delete an active
synthetic home while its App/Harness still owns it. See
[runtime-storage-operations.md](runtime-storage-operations.md).
