# Client experience and state projection

Read for conversation, native, browser, or operations clients. Choose the product's
experience and existing stack before implementation. These contracts are platform
neutral; use [browser-experience.md](browser-experience.md) or
[native-cli-client.md](native-cli-client.md) only for the selected adapter.

## Inspect and preserve the real product

Map the actual launcher, identity/session client, command transport, state/event
projection, composer, messages, settings, uploads, evidence and download handlers to
source and tests. Record source/build/running identities and existing dirty/untracked
files. A template, compiled preview, or renamed route is not an integrated product.
Reuse the existing Runtime, model/tool gateways, authorization and canonical store;
do not introduce a second chat controller or simulated completion timers.

Select the visual hierarchy from the user's reference and product intent:

- **Conversation first:** composer and messages are primary; source/model/mode
  selectors are light; settings belong behind an account/settings entry; evidence,
  tools and diagnostics appear when relevant rather than as empty permanent panels.
- **Operations console:** expose operational navigation only when requested for
  that audience. Do not impose a dense management dashboard on end users.

Language, navigation labels, branding, pixel values and theme defaults belong to the
project profile. Borrow interaction/layout patterns without copying unrelated paid,
voice, IDE or account features. Migrate real forms and handlers, not just styles;
hidden legacy views must not continue polling. UI relocation never lowers backend
roles, workspace scope or deep-link authorization.

## Canonical client contract

Commands identify actor/session/run, correlation and idempotency keys, and expected
version/epoch where applicable. Identity, source grants and permissions come from
the authenticated host, not model or frontend assertions. Project one authoritative
snapshot/event stream; maintain stable message IDs and sequence cursors.

| Action | Required semantics |
|---|---|
| New/open conversation | Switch context without implicitly cancelling an existing run |
| Send or submit Ask User | Stable request/input ID; duplicate clicks cannot repeat effects; resume the original run |
| Pause/resume/stop | ACK means accepted, not confirmed; display request-pending until the Runtime confirms |
| Reconnect | Restore snapshot/cursor/sequence before consuming later events; deduplicate final/results |
| Change account/scope | Fence stale responses/streams/uploads before applying them to the new identity |
| Open/close settings | Preserve drafts, attachments and active work; dirty-state checks for unsaved settings |
| Evidence/download | Resolve authorized opaque refs, never a model-provided path or filename |

Controls reflect real states: show actions meaningful for the current run and keep
Stop reachable while running. Closing a view or disconnecting transport is not a
cancel operation. A cancelled/revoked run cannot accept late content or claim success.
Keep partial, unknown, unverified and errors visible where they affect conclusions;
normal users need safe summaries, not raw trace, credentials or hidden reasoning.

## Forms, identity, sources and input ownership

- Preserve the requested authentication model. Do not replace token-only auth with
  password auth without authorization, or fake sign-in locally. When personal
  accounts are required, complete registration/sign-in/recovery/logout against the
  real identity service and explain the actual recovery mechanism; do not invent
  email delivery. Secrets use secure fields and host storage, never argv/logs.
- Separate registered connections from pending selection, confirmed session scope
  and immutable run pins. Multi-select Confirm commits atomically; Cancel keeps the
  old selection; an empty selection must not silently retrieve every source.
  Changing sources cannot rewrite an active run or revive incompatible old context.
  Use [document-source-pipelines.md](document-source-pipelines.md).
- Upload through the existing choose/transfer/finalize/source-binding pipeline.
  Support the promised formats, multiple/long names and stage errors. Do not add
  arbitrary UI limits or read a large binary wholly for preview. Removing an item
  fences its late completion. Attachment presence is independent of a Wiki mount.
- Select only authorized model/skill/context entries; changing a menu must not
  probe a model, load all knowledge or make an inference request. Shortcuts that
  draft a task must remain editable until explicitly sent.
- Track busy/error callbacks by request and scope. Reject double submission; an
  old callback cannot release a newer request's pending state or reuse a previous
  database's field mapping. Disabled buttons need an actionable validation reason.
- Theme foreground/background, hover, pressed and disabled states explicitly.
  Avoid unreadable primary buttons. Respect requested mouse focus styling while
  retaining visible keyboard focus, tab order, activation and accessibility.
- Constrain dialog focus; Escape closes only the top layer; closing returns focus
  to a visible opener. Settings must fit narrow windows rather than overflow.
- Treat IME marked/composing text separately from committed text: placeholder is
  hidden during composition, Return confirms a candidate before sending, and
  ordinary state refresh never cancels or overwrites composition. Test with the
  actual input method when that behavior is a requirement.

## Rich messages and streaming

One canonical content-parts contract feeds one renderer pipeline. Preserve original
text/Markdown separately from display and retain evidence/artifact IDs. Extract the
answer from protocol envelopes; do not display the entire transport JSON. Ordinary
user text remains literal unless the product explicitly requests rich user input.
Rendering must not change stored text or trigger model/Reader calls.

| Surface | Implementation and negative checks |
|---|---|
| Markdown | Headings, emphasis, lists/nesting/tasks, quotes, rules, links, inline/fenced code, GFM tables, Unicode; preserve whitespace and syntax instead of regex-stripping it |
| Code | Accurate indentation/newlines, language label/highlighting, Copy code, internal scroll; unknown languages fall back to inert source; never auto-execute |
| Tables | Real rows/cells, bounded internal horizontal/vertical layout, complete original-Markdown copy; no implied spreadsheet editor |
| Math/diagrams | Load only selected compatible renderers; validate complete blocks, resource limits and safe configuration; unsupported LaTeX/diagram syntax returns source with an explicit limitation |
| Partial streams | Incomplete fences, emphasis, tables, math, links and mixed-language chunks remain safe; deltas append to one message buffer using ID/sequence |
| History/actions | Initial, final and restored source agree; Copy/Copy Markdown/Regenerate/Feedback use real callbacks and full source, not truncated previews or HTML |
| Evidence | Only authoritative IDs open exact authorized source/page/object/range; an `[Evidence]` string, SKU or filename creates no authority |
| Tool cards | Real Runtime events, allowed summaries/duration/error/artifacts, separate from final answer; no invented progress or raw sensitive arguments |
| Images/artifacts | Authorized artifact routes; shown image/version/region matches the one used for analysis; invalid refs stay visibly unavailable |

Do not execute HTML/scripts, event handlers, iframes or dangerous URL schemes from
messages. Unknown external images/tracking pixels do not auto-load. Keep external
links distinct from internal artifacts and use the product's link confirmation
policy. Do not send private messages to third-party rendering services. Large
previews may be limited, but complete-copy/export and scope/verification semantics
must remain honest. A text fallback is not proof of full math/diagram support.

Buffer/coalesce deltas without reparsing all history or reconstructing the App on
every token. Defer heavy highlighting/diagrams; final render uses complete source.
Follow the stream only near the bottom; preserve a user's upward scroll and offer
Jump to latest. Cancellation/recovery preserves already public content without
duplicate messages. Component delta stress tests are distinct from real transport
streaming, and narrow component tests do not establish a mobile product.

## Acceptance and handoff

Use the actual primary product in an isolated synthetic account/scope, not a second
reduced backend. Verify login/session/logout, draft/settings roundtrip, uploads and
same-file follow-up, Ask User, source selection/revoke, control confirmation,
reconnect/late events, citations/downloads, themes, keyboard/IME and long messages.
Adapt the rich-message matrix to promised features rather than requiring every
renderer/plugin in every client. Test deep-link/command authorization independently
of hidden UI buttons. See [testing-and-evaluation.md](testing-and-evaluation.md).

After the final relevant source/prompt/UI change, record source, build, packaged and
actually loaded identities. Native or browser delivery checks belong to its adapter
reference. Preserve old failures and mark blocked/unverified surfaces precisely;
screenshots, templates, component tests and a user saying a window is visible do
not establish full functional E2E.
