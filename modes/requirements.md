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

- `features/*/references.md`
- `features/*/slices/*/slice.md`
- `features/*/slices/*/requirements/frontend.md`
- `features/*/slices/*/requirements/backend.md`
- `features/*/domain-impact.md`


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
