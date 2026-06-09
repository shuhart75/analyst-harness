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

## Requirement format selection

Before generating or substantially rewriting requirements, choose one format:

- `new readable` / `новый лёгкий формат`: use `feature-requirements.readable.template.md`, `slice.readable.template.md`, `frontend.readable.template.md`, `backend.readable.template.md`.
- `old detailed` / `старый подробный формат`: use `feature-requirements.template.md`, `slice.template.md`, `frontend.template.md`, `backend.template.md`.

Selection rules:

- If the user explicitly says `новый формат`, `лёгкий формат`, `как deployments`, `краткие срезы`, use the new readable templates.
- If the user explicitly says `старый формат`, `подробный формат`, `как раньше`, use the old detailed templates.
- If the user does not specify a format and the feature already has requirements, preserve the feature's current format.
- If the user does not specify a format and this is a new feature, use the new readable format by default.
- Do not mix formats inside one feature unless the user explicitly asks for a migration or a partial experiment.
- Diagrams in either format must be PlantUML, not Mermaid.

## Main outputs

- `features/*/requirements.md`
- `features/*/references.md`
- `features/*/slices/*/slice.md`
- `features/*/slices/*/requirements/frontend.md`
- `features/*/slices/*/requirements/backend.md`
- `features/*/domain-impact.md`
- `features/*/context-summary.md`
- `features/*/artifact-map.md`
- `features/*/slices/*/context-summary.md`
- optional `features/*/.research/*` and `features/*/slices/*/.research/*`

## Source-of-truth rule

- `features/<feature>/requirements.md` is the primary and authoritative requirements document for the feature.
- Slice cards and FE/BE packs are derived artifacts. They are not authored as independent parallel truths.
- If a slice pack reveals a missing rule, contradiction, or new requirement, update the root feature document first and only then re-derive the slice artifacts.
- Context summaries, artifact maps and `.research/` files are auxiliary. Accepted findings must be transferred into the root feature document, slice packs, `domain-impact.md` or `.workflow/consistency-backlog.md`.

## Writing order

1. Create or update the root feature document `features/<feature>/requirements.md`.
2. Fix semantic slice boundaries and explicit slice order there.
3. Create or update `slices/*/slice.md` as decomposition cards derived from the root document.
4. Create or update `slices/*/requirements/frontend.md` and `slices/*/requirements/backend.md` as detailed annexes derived from the corresponding root section.
5. Do not invent slice scope that is absent from the root feature document without editing the root feature document first.

The root feature document must follow the selected root template. The old detailed root template is `.workflow/templates/requirements/feature-requirements.template.md`; the new readable root template is `.workflow/templates/requirements/feature-requirements.readable.template.md`.

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

## Small-context requirements rules

For `делаем требования`, `актуализируй требования`, `разложи требования на срезы` and `подготовь детальные требования по срезам`, the assistant must automatically:

- read existing feature/slice context summaries and artifact map when present;
- create or refresh `features/<feature>/context-summary.md` after substantial root requirement changes;
- create or refresh `features/<feature>/artifact-map.md` when authored, derived or auxiliary artifacts change;
- create or refresh `features/<feature>/slices/<slice>/context-summary.md` when a slice card or FE/BE pack is created or materially changed;
- run role-based research from `.workflow/research-policy.md` when requirements are large, ambiguous, cross-cutting, or code/source-material inspection is needed;
- run the completeness checklist before presenting slice requirements as ready;
- update a checkpoint before and after long decomposition or derivation passes.

Do not expose `собери контекст`, `исследуй срез` or `проверь полноту среза` as required user commands. Ask the user only when research finds a contradiction, missing business decision, prototype mismatch, neighboring-feature impact or required root requirement change.

## Forbidden without mode switch

- changing agreed planning estimates
- changing quarter or commander baseline gantt
- changing actual execution dates
