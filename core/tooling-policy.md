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
- After requirement edits, use targeted text search or an equivalent local find-in-files sweep for superseded terms such as old endpoints, field names, role names, status values and UX labels.
- Keep the sweep proportional: start with the current feature and explicitly affected artifacts; expand to neighboring features or baseline only when the change is cross-feature or domain-wide.
- If the project provides `.workflow/tools/find-stale-terms.py`, use it as the fast default helper for local tail cleanup; otherwise use the platform's normal text search.
- If the user asks for a PlantUML file "without includes" or Confluence-ready code, expand `!include` directives with `.workflow/tools/expand-plantuml-includes.py` when available instead of editing generated gantt sources by hand.

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
