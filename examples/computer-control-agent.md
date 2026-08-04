# Computer-control agent: bounded UI automation

## Goal

Operate a browser or desktop application while preventing credential, privacy, and destructive-action misuse.

## Control loop

Observe screenshot/accessible tree → identify target and confidence → propose one action → apply permission/approval → execute → observe state change → verify expected UI state → checkpoint. Limit actions, elapsed time, retries, downloads/uploads, and domains/apps.

## Permission classes

- read-only navigation and inspection: allow within approved app/domain;
- form edits that are reversible: ask according to policy;
- submit/send/purchase/delete/install/credential entry: always preview exact target/content and require scoped approval;
- password/cookie extraction, hidden data access, policy changes, or OS escape: deny.

## Verification

Use accessible properties and screenshot artifacts, not visual assumption alone. Confirm the intended element, recipient/account, and post-action state. For non-idempotent submits, reconcile after timeout rather than retrying blindly.

## Tests

Ambiguous target, stale UI, pop-up/domain change, indirect prompt injection in page content, hidden sensitive field, approval rejection/expiry, network loss after submit, download scanning, and tenant-isolated browser profiles.
