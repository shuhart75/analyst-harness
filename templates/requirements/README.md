# Requirement Pack Templates

This directory contains the canonical requirement pack templates used by the harness.

## What lives here

- `feature-requirements.template.md` — root feature requirement page for control and review
- `slice.template.md` — semantic slice card derived from the root feature page
- `frontend.template.md` — FE requirement pack
- `backend.template.md` — BE requirement pack

## Where the active project template lives

When a project is scaffolded, these templates are copied into:

- `.workflow/templates/requirements/feature-requirements.template.md`
- `.workflow/templates/requirements/slice.template.md`
- `.workflow/templates/requirements/frontend.template.md`
- `.workflow/templates/requirements/backend.template.md`

Project-local copies are the templates that the LLM should follow when writing or updating requirements.

## Writing rules

- Write requirement packs in Russian by default.
- Keep slugs, paths, ids and technical identifiers in English.
- Use the root feature page as the primary control document and single authored source.
- Derive slice cards and FE/BE packs from the corresponding sections of `features/<feature>/requirements.md`.
- Do not invent new slice scope independently from the root feature page.
- Treat requirements as living artifacts until release finalization.
- Keep business rules, system rules, acceptance criteria, API contracts and examples traceable to source materials.
- If a change affects neighboring features, baseline artifacts or prototypes, update `domain-impact.md` and `.workflow/consistency-backlog.md` in the same turn.

## Minimal workflow

1. Create or update `features/<feature>/requirements.md` by `feature-requirements.template.md`.
2. Fix the explicit slice order and section boundaries there.
3. Create or update `slices/*/slice.md` as a decomposition map derived from the root document.
4. Fill `requirements/frontend.md` and/or `requirements/backend.md` as detail annexes for each slice section.
5. Link the relevant prototypes.
6. Register consistency impact in `features/<feature>/domain-impact.md`.
