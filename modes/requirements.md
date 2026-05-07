# Mode: requirements

## Goal

Produce or update living requirement packs from canonical baseline, source materials and change requests.

## Main inputs

- `.workflow/templates/requirements/`
- `baseline/current/`
- `context/source-materials/current-system/requirements/`
- `context/source-materials/current-system/screenshots/`
- `context/source-materials/current-system/prototypes/`
- `context/source-materials/current-system/diagrams/`
- `context/source-materials/change-requests/`

Use `.workflow/templates/requirements/` as the active project-local template source. Do not write requirement packs freeform when these templates exist.

## Main outputs

- `features/*/requirements.md`
- `features/*/references.md`
- `features/*/slices/*/slice.md`
- `features/*/slices/*/requirements/frontend.md`
- `features/*/slices/*/requirements/backend.md`
- `features/*/domain-impact.md`

## Source-of-truth rule

- `features/<feature>/requirements.md` is the primary and authoritative requirements document for the feature.
- Slice cards and FE/BE packs are derived artifacts. They are not authored as independent parallel truths.
- If a slice pack reveals a missing rule, contradiction, or new requirement, update the root feature document first and only then re-derive the slice artifacts.

## Writing order

1. Create or update the root feature document `features/<feature>/requirements.md`.
2. Fix semantic slice boundaries and explicit slice order there.
3. Create or update `slices/*/slice.md` as decomposition cards derived from the root document.
4. Create or update `slices/*/requirements/frontend.md` and `slices/*/requirements/backend.md` as detailed annexes derived from the corresponding root section.
5. Do not invent slice scope that is absent from the root feature document without editing the root feature document first.

The root feature document must follow `.workflow/templates/requirements/feature-requirements.template.md`, which is based on the user's Confluence-compatible requirement page structure.

## Tail cleanup rule

If the task replaces one requirement variant with another, remove stale mentions of the superseded variant in the same turn inside:

- `features/<feature>/requirements.md`;
- `features/<feature>/slices/*/slice.md`;
- `features/<feature>/slices/*/requirements/frontend.md`;
- `features/<feature>/slices/*/requirements/backend.md`;
- `features/<feature>/domain-impact.md` and `.workflow/consistency-backlog.md` when they describe the replaced variant.

Examples of stale tails to search for:

- old endpoint paths;
- old request or response field names;
- old role names;
- old status names;
- old UX control names or option labels;
- old contract filenames or Decision IDs.

## Two-speed consistency sweep

Keep consistency work proportional to the size of the change.

- For a small local edit, do a quick feature-local sweep with targeted text search or equivalent local find-in-files and stop when the changed feature is clean.
- For domain, lifecycle, role, API-semantic, shared-UI or neighboring-feature changes, expand into a full sweep with `domain-impact.md`, `.workflow/consistency-backlog.md`, and affected baseline artifacts.
- Do not turn every minor wording fix into a whole-repo audit.

## Impact detection requirement

Any requirement change must be checked for consistency impact.

If the change affects domain rules, lifecycle, roles, API semantics, data model, neighboring features, or shared UI behavior:
- update `features/*/domain-impact.md`;
- list affected requirements and prototypes;
- update `.workflow/consistency-backlog.md` when propagation is deferred;
- do not silently mutate `baseline/current/` unless the active task explicitly includes baseline update.

## Forbidden without mode switch

- changing agreed planning estimates
- changing quarter or commander baseline gantt
- changing actual execution dates
