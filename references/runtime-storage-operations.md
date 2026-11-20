# Runtime storage, migration and scoped cleanup

Read for installation paths, resource migration, cache cleanup, container/VM storage
or retirement. This is an operator workflow, not permission for an Agent tool to
scan arbitrary host paths or delete resources. Use the user's current scope and
repository policy; do not turn a past install grant into permanent reinstall rights.

## Audit before mutation

- Resolve the real project and configured private resource roots from their single
  owner. Do not derive persistent paths independently from cwd/HOME in launchers,
  workers and tools. Inspect call sites, configs, environment loading and locks.
- Record exact ownership, type, inode/link/symlink metadata, allocated/logical size,
  active processes/handles, consumer/dependency references and current capability
  states. Do not read private key contents, real business data or unrelated homes.
- Preserve a limited recoverable source/config diff including untracked program
  files. Runtime/private data requires its own authorized policy; a source patch is
  not a data backup. Keep QA outside product source and private runtime out of Git,
  distribution archives, logs and screenshots.
- Classify KEEP, confirmed disposable CLEAN, proven ORPHAN, REBUILDABLE, or BLOCKED.
  A stopped profile, zero running containers or unattached volume alone proves none
  of orphanhood. Trace on-demand consumers before deleting their dependencies.

## Migration contract

Move only explicitly named resources after safe shutdown/exclusive ownership.
Update real configuration, launcher, CLI, worker, tool and installer paths through
the common resolver; do not merely move directories or add compatibility symlinks
that preserve obsolete behavior. Reject escapes and unexpected link/type changes.
Account/profile/state identity and encrypted payload compatibility must survive.

Check platform constraints such as Unix-domain socket length, not only directory
existence. A short supported runtime-root override can preserve the same resource;
it is not a second VM. Verify a cold/repeat primary launch and relevant CLI/tools,
then assert old paths stay absent. Migration and deletion have separate rollback
records. Do not reset/clean the repository or touch another project to simplify it.

## Virtual disks and container dependencies

Separate logical capacity, allocated blocks, filesystem free space and global host
free capacity. Inspect disk format/backing relationships and configured root versus
additional/data disks. Similar sizes do not establish duplicates. Distinct inodes
rule out hard links, not shared APFS extents/clones. Ordinary copies can expand
sparse allocation; avoid creating giant backups without purpose/authorization.

Bind every engine command to the verified private profile and socket/context,
including its environment. Do not trust a global default daemon. Inventory image
IDs/digests, shared/unique layers, build cache, containers, named volumes and owner
labels. Required on-demand images can be called reclaimable by generic tools;
never sum shared layer sizes or prune that label blindly. Persistent volume content
is not disposable simply because a container is stopped.

Prefer confirmed cache cleanup while preserving required resources. Use only the
installed version's supported trim/cleanup commands and record their real exits.
Measure before start, after automatic startup work, after cleanup/trim and after
normal stop/restart as appropriate. Discard/trim output is not host bytes freed;
global free-space deltas include concurrent activity. Report allocated reduction
with these limitations rather than claiming the disk's logical capacity was freed.

## Explicit retirement and deletion

When the user explicitly chooses to retire a dependency, explain the exact lost
capabilities/data, preserve required unrelated resources, and use the supported
exact-profile teardown. Apply the persistent gate in
[capability-readiness.md](capability-readiness.md) so health checks, recovery,
install/provision and old probes cannot resurrect it. Do not retain an equally
large disk copy contrary to an explicit authorized disposal request, and do not
claim rollback when deleted volume data cannot be restored.

For leftover cleanup, use an exact reviewed target/entry allowlist, owner/type and
identity checks, and empty handle/process checks. Do not use global Docker prune,
unbounded recursive deletion, or deletion by filename resemblance. A changed or
unknown entry stops that deletion for review. Preserve partial failure records and
check the actual remaining objects before a bounded retry; do not assume a failed
helper made no changes.

## QA cleanup and final evidence

Close the task's App/Harness/workers before deleting its synthetic home. Remove only
task-owned temporary accounts, data, mock sparse disks, containers and caches, not
formal runtime resources. Keep compact command/exit records, hashes, failure logs
and limited source beforeimages. Installation or tests must not leave orphan
processes, repeated temporary instances or large unused caches.

After mutation, remeasure and verify the actual affected primary paths: login and
identity, text conversation/model connection, generic files/artifacts, relevant
tools and control/cancellation. A retired function passes by staying Disabled and
not recreating resources, not by rerunning its former success algorithm. Report
what was not tested. Operational recovery may require fresh authorization to
reinstall/reconfigure; source restoration alone cannot recover deleted data.
