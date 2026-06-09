# Mode: planning

## Goal

Shape a feature for quarter-level planning and HLE.

The planning mode starts with feature intake when the user brings a candidate new feature from an external folder or an unstructured initiative.

## Main artifacts

- `planning/intake/*.md`
- `.workflow/templates/intake/feature-intake.template.md`
- `.workflow/templates/planning/planning-context.template.md`
- `.workflow/templates/planning/assumptions.template.md`
- `.workflow/templates/planning/risk-register.template.md`
- `.workflow/templates/planning/story-map.template.md`
- `.workflow/team.md`
- `features/*/feature.md`
- `features/*/planning/planning-context.md`
- `features/*/planning/assumptions.md`
- `features/*/planning/risk-register.md`
- `features/*/planning/story-map.md`
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
- planning context, assumptions, risk register and story map

## Estimation rules

- `features/<feature>/planning/estimates.md` must not contain only one undifferentiated story estimate.
- For every planning story, store estimates by role in the format `AN / FE / BE / QA`.
- Keep `Agreed total, дн` as a control sum of the agreed role estimates.
- QA may be `0` only when testing was explicitly not estimated or is tracked outside the feature; do not omit the QA column.

## Gantt planning rules

- Feature sections are the primary visual grouping in quarter, commander and actual-progress gantt views.
- When planning future not-started work for a feature, put backend/API work before frontend work.
- If exact dates are not known, plan frontend no earlier than 3 open days after backend/API work starts.
- Use `.workflow/team.md` as the team roster. Default lanes are `A1-A3`, `B1-B3`, `F1-F2`, `Q1-Q3`.
- Do not plan more than one full-time task on the same resource for the same open day. Use available resources as fully as possible before pushing work later.
- Use canonical resource lanes when a resource is known: `A<N>`, `B<N>`, `F<N>`, `Q<N>`. Keep aliases only as input shorthand, not as the preferred written form.

## Current-state actualization boundary

Planning mode owns quarter and commander baselines. It does not own current execution state.

- `спланируй квартал`, `собери командирский план`, HLE and planning stories may update quarter-plan and commander-plan.
- `обнови реальный прогресс`, `обновляем прогресс`, task statuses, actual dates, execution resources and actual-progress gantt belong to `execution-update`.
- If the user asks to актуализировать текущее положение дел while planning mode is active, switch to `execution-update` before changing tasks or actual-progress.
- Do not silently edit `quarter-plan.puml` or `commander-plan.puml` while only updating current state.

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

## Small-context planning rules

Planning work must automatically maintain enough context for a small-window LLM to resume without rereading all source materials.

For `новая фича`, `занимаемся планированием`, `спланируй фичу`, `подготовь HLE`, quarter-plan and commander-plan work:

- summarize source materials into the intake result or `features/<feature>/planning/planning-context.md`;
- explicitly separate current-system coverage, new delta and uncertain items;
- keep planning assumptions in `features/<feature>/planning/assumptions.md` or a clearly named section of `planning-context.md`;
- keep planning risks in `features/<feature>/planning/risk-register.md` or a clearly named section of `planning-context.md`;
- map `source -> delta -> planning story -> slice` in `features/<feature>/planning/story-map.md` when the feature is large enough that the relationship is not obvious;
- update the run checkpoint before and after long planning passes.

Do not ask the user to request these context operations explicitly. Ask only when scope, quarter boundary, estimate basis or current-vs-new classification requires a human decision.
