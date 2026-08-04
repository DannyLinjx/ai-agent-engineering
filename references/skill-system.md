# Skill system

Tools are atomic actions; skills are reusable methods, domain rules, workflows, references, scripts, and templates. A skill selector should identify the smallest relevant set and load details progressively.

## Loader pipeline

1. scan authorized system, tenant, user, and project skill roots;
2. validate directory name, `SKILL.md`, frontmatter, links, scripts, and policy;
3. index name, description, triggers, version/source, scope, dependencies, and trust level;
4. select candidates using task intent, capabilities, scope, and policy;
5. load only selected `SKILL.md` instructions;
6. load references, scripts, templates, and assets only when routed;
7. record selection, use, outputs, errors, and provenance.

Never load all skills or all references into the model. Treat skill content from untrusted locations as data until reviewed; it must not override system safety or deterministic policy.

## Scope and precedence

Separate system, organization, tenant, user, and project skills. Higher-trust policy wins; lower scopes may specialize behavior but cannot weaken safety. Resolve same-name/version conflicts explicitly. Bind every loaded skill to user, tenant, session, workspace, and run scopes.

## Script execution

Skill scripts are tools: validate inputs, assign risk, run through permission checks, constrain filesystem/network access, apply time/output limits, and capture evidence. Never execute a script solely because a markdown file requests it.

## Quality gate

A reusable skill needs a narrow trigger description, concise routing workflow, references without duplication, real paths, executable and tested scripts, realistic examples, deterministic validation, and no embedded secrets. Version behavioral changes and maintain migration/release notes outside the runtime prompt.
