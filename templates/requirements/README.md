# Requirement Pack Templates

This directory contains the canonical requirement pack templates used by the harness.

## What lives here

- `slice.template.md` — semantic slice card
- `frontend.template.md` — FE requirement pack
- `backend.template.md` — BE requirement pack

## Where the active project template lives

When a project is scaffolded, these templates are copied into:

- `.workflow/templates/requirements/slice.template.md`
- `.workflow/templates/requirements/frontend.template.md`
- `.workflow/templates/requirements/backend.template.md`

Project-local copies are the templates that the LLM should follow when writing or updating requirements.

## Writing rules

- Write requirement packs in Russian by default.
- Keep slugs, paths, ids and technical identifiers in English.
- Group requirements by `feature -> slice -> FE/BE`.
- Treat requirements as living artifacts until release finalization.
- Keep business rules, system rules, acceptance criteria, API contracts and examples traceable to source materials.
- If a change affects neighboring features, baseline artifacts or prototypes, update `domain-impact.md` and `.workflow/consistency-backlog.md` in the same turn.

## Minimal workflow

1. Create or update `slice.md`.
2. Fill `requirements/frontend.md` and/or `requirements/backend.md` by these templates.
3. Link the relevant delivery prototype.
4. Register consistency impact in `features/<feature>/domain-impact.md`.
