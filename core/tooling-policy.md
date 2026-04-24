# Tooling Policy

## Tool selection

Prefer the simplest tool that preserves auditability.

- Use markdown as the source of truth for planning, requirements, execution mapping and release notes.
- Use generated PlantUML only for gantt rendering, not for storing semantic mapping.
- Keep raw evidence in `context/source-materials/`.

## Validation discipline

After structural or canonical changes, run available validators.
After gantt-related changes, regenerate the gantt.
After release promotion, validate both structure and links again.

## Editing discipline

- Prefer small explicit edits over large opaque rewrites.
- Do not regenerate unrelated files just because a tool can.
- Preserve human-readable names in markdown; keep slugs and ids stable.

## CLI-neutrality

Do not assume a specific terminal agent supports:
- subagents;
- skills;
- memory;
- local plugins.

When such capabilities exist, use them as optional accelerators, not as the only workflow path.

## Consistency records

- `features/*/domain-impact.md` stores per-feature impact and affected artifact lists.
- `.workflow/consistency-backlog.md` stores unresolved or deferred propagation work, including prototype drift and rollback propagation.
- Do not hide known inconsistency in chat only; record it in one of those files.
