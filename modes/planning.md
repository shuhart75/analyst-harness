# Mode: planning

## Goal

Shape a feature for quarter-level planning and HLE.

The planning mode starts with feature intake when the user brings a candidate new feature from an external folder or an unstructured initiative.

## Main artifacts

- `planning/intake/*.md`
- `.workflow/templates/intake/feature-intake.template.md`
- `features/*/feature.md`
- `features/*/planning/stories/*.md`
- `features/*/planning/estimates.md`
- `features/*/planning/scope-prototype/*`
- `features/*/domain-impact.md` for preliminary DDD impact
- `planning/*/gantt/quarter-plan.puml`
- `planning/*/gantt/commander-plan.puml`

## Allowed changes

- feature intake / preflight notes
- planning stories
- preliminary domain impact
- analyst/team/agreed estimates split by `AN / FE / BE / QA`
- scope prototype
- quarter and commander gantt

## Estimation rules

- `features/<feature>/planning/estimates.md` must not contain only one undifferentiated story estimate.
- For every planning story, store estimates by role in the format `AN / FE / BE / QA`.
- Keep `Agreed total, дн` as a control sum of the agreed role estimates.
- QA may be `0` only when testing was explicitly not estimated or is tracked outside the feature; do not omit the QA column.

## Preliminary impact

During planning, capture obvious cross-feature or domain-wide consequences in `domain-impact.md`, but keep them marked as `proposed` until requirements work confirms them.

## Forbidden without mode switch

- implementation task actual dates
- execution status tracking
- actual-progress gantt


## Feature intake rule

When the user says `новая фича` or otherwise points to an external folder and says this is a new feature:

- do not scaffold `features/<slug>/` yet;
- do not create slices yet;
- inspect the source materials first;
- compare them against `baseline/current/`, existing `features/*`, and legacy/source-materials planning where relevant;
- separate existing coverage from the true new delta;
- write the result to `planning/intake/<candidate-slug>.md` using `.workflow/templates/intake/feature-intake.template.md`;
- only after intake confirmation proceed to feature scaffolding and planning stories.
