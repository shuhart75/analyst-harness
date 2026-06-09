# LLM Contract

This contract is CLI-neutral. It applies to Codex CLI, Claude Code, Qwen CLI, VSCodium agents, and other LLM assistants working in a project scaffolded with this harness.

## Session bootstrap

Before changing artifacts, read:

1. `AGENTS.md`
2. `.workflow/llm-contract.md`
3. `.workflow/agent-delegation.md`
4. `.workflow/skills-policy.md`
5. `.workflow/tooling-policy.md`
6. `.workflow/context-policy.md`
7. `.workflow/research-policy.md`
8. `.workflow/active-mode.md`
9. `.workflow/modes/<active-mode>.md`
10. `.workflow/team.md` before planning resources or regenerating actual-progress
11. relevant `.workflow/overrides/*.md`
12. `.workflow/templates/intake/` when the user brings a candidate new feature
13. `.workflow/templates/requirements/` when working in requirements mode
14. `.workflow/templates/prototypes/` when working in prototype modes
15. `.workflow/templates/context/` when creating or refreshing feature/slice context
16. `.workflow/templates/research/` when role-based research is needed
17. `baseline/current/` for the canonical deployed state when it exists
18. relevant `features/<feature>/context-summary.md` and `artifact-map.md` when present
19. relevant `features/<feature>/feature.md`, root requirements, root prototype, slice artifacts, planning stories, execution tasks and gantt includes
20. relevant `releases/` artifacts when finalizing a delivered change

If the user points to a folder with current-system docs/screenshots/change requests, inspect that folder first and keep source references in the produced artifacts.


## Small-context operating rules

Treat context management as an internal harness responsibility. Users should not have to request context summaries, checkpoints, research, completeness sweeps, or prototype/slice alignment checks.

When work is broad, long-running, or likely to exceed a small context window:
- read existing `context-summary.md`, `artifact-map.md`, planning context and run-state files before broad source artifacts;
- create or refresh feature/slice/planning/execution context summaries when source-of-truth artifacts change substantially;
- update `.workflow/run-state/current.md` or an equivalent checkpoint before and after long passes;
- keep facts, inferences, assumptions and open questions separate;
- transfer accepted research findings into authoritative artifacts instead of leaving them only in `.research/` or chat.

External memory systems are optional accelerators. Repository markdown remains the source of truth.


## Command interpretation rules

Treat short natural-language workflow commands from `.workflow/command-catalog.md` as first-class instructions.

When the user uses a command from that catalog or a near-equivalent phrase:
- map it to the intended workflow mode and action;
- switch mode if needed;
- read the target mode file before editing;
- execute the implied workflow, not just the literal words;
- preserve the user's concrete names, dates, task ids and paths.

If the command references impacted requirements, prototypes, or rollback of a known decision, consult:
- `features/*/domain-impact.md`;
- `.workflow/consistency-backlog.md`;
- `releases/*` and `baseline/current/` when relevant.

If multiple commands conflict, prioritize the most recent explicit user instruction and state the assumption briefly.

## Feature intake rule

Treat `новая фича` as a first-class planning command.

When the user says `новая фича`, or gives a folder and says this is a new feature:
- switch into `planning` mode if needed;
- do not scaffold `features/<slug>/` yet;
- inspect the folder first;
- compare the candidate change against `baseline/current/`;
- compare it against existing `features/*`;
- compare it against legacy planning and source materials when relevant;
- separate existing system coverage from the true new delta;
- write the result to `planning/intake/<candidate-slug>.md` using `.workflow/templates/intake/feature-intake.template.md`;
- return proposed feature slug, proposed slices, affected baseline artifacts, affected existing features, Q2 scope draft, and workflow gaps before any scaffold step.

Only create the feature structure after the intake result is accepted or the user explicitly asks to proceed.

## Modes are guardrails

Treat the active mode as a write boundary.

- `planning`: owns feature scope, planning stories, estimates, scope prototype, quarter-plan and commander-plan.
- `requirements`: owns slices and FE/BE requirement packs.
- `scope-prototype`: owns planning-stage live prototypes for customer scope alignment.
- `delivery-prototype`: owns slice-level React + MUI prototypes for frontend handoff.
- `execution-update`: owns implementation tasks, actualization mapping, and actual-progress gantt.
- `release-finalization`: owns release packages, final requirements, baseline promotion, and canonical baseline updates.

If the user asks for work outside the active mode, either switch mode explicitly or state the cross-mode change before editing.

## Canonical entities

- `baseline/current` is the canonical deployed-system description.
- `planning story` is a planning/HLE unit. It has Summary, Description, estimates split by `AN / FE / BE / QA`, and may not match implementation tasks 1:1.
- `implementation task` is an execution tracking unit. It should match Jira naming where possible and includes estimate, dates, executor, status and progress.
- `requirement pack` is grouped by feature/slice and then FE/BE.
- `features/<feature>/requirements.md` is the primary control page and authored source for requirements; each slice must have its own ordered section there.
- `slice card` and slice FE/BE packs are derived artifacts cut from the root feature requirements, not parallel independent sources.
- `common feature prototype` lives in `features/<feature>/prototype.html`; the user iterates on it first as the visual source of truth.
- `delivery prototype` is a slice-level schematic handoff artifact derived from the confirmed common feature prototype and root requirements.
- `release package` captures the final delivered state before promotion into a new baseline.

## Gantt rules

- `quarter-plan` and `commander-plan` are built from planning stories.
- Planning story estimates must be stored in `features/<feature>/planning/estimates.md` with explicit `AN / FE / BE / QA` role splits and an agreed total.
- `commander-plan` is the quarter plan with management buffer, normally 20-30%.
- `actual-progress` must show two useful layers:
  - `PLAN <TYPE> <summary>` bars from commander-plan planning stories;
  - current execution tasks, virtual or real.
- Do not put square brackets in PlantUML task labels. Use `PLAN FE ...`, not `PLAN [FE] ...`.
- Feature sections on generated root gantt files must be separated by `-- Feature title --`.
- Root gantt files must include the marker `Мы сейчас здесь`.
- Project start is quarter start, unless a visible task starts earlier.
- Do not hide baseline planning stories from actual-progress; the diagram exists to compare plan vs fact.
- Put hand-authored milestones in view-specific preamble files, for example `planning/<quarter>/gantt/preamble/actual-progress.puml`, not in generated root gantt files.
- When a milestone uses `happens at YYYY/MM/DD` in a preamble, `sync-quarter-gantt.py` should highlight that day in the generated view.
- If the user asks for a standalone PlantUML export without includes, expand the generated view into a separate file and leave the include-based source intact.
- For actual-progress execution tasks, tasks that have `Progress % = 0` and no actual dates are not allowed to render in the past. On each regeneration, the generator moves their rendered start to today, or the next open day, without changing the markdown source dates.
- Within one feature section, not-started backend/API tasks should lead not-started frontend tasks. Frontend tasks may render no earlier than 3 open days after the earliest not-started backend task in the same feature.
- Not-started execution tasks must not overload resource lanes. Use `.workflow/team.md` as the roster, keep each resource at no more than one full-time task per open day, and use available resources as fully as possible before pushing work later.
- If a not-started task has no explicit executor, has a `TBD_*` executor, or references a non-roster resource lane, assign it by role from `Role`, task id prefix, executor alias or summary. Preserve explicit valid roster lanes, but still shift dates if needed to avoid overload.
- Keep baseline `PLAN ...` story bars visible for plan-vs-fact comparison even when execution tasks are shifted forward by the current date.

## Resource naming

- Role estimates and semantic task roles use `AN / BE / FE / QA`.
- The project-local roster lives in `.workflow/team.md`.
- Default PlantUML resource lanes are `A1`, `A2`, `A3`, `B1`, `B2`, `B3`, `F1`, `F2`, `Q1`, `Q2`, `Q3`.
- Accepted aliases for resource/executor input:
  - analyst: `A`, `AN`, `analyst`, `аналитик`;
  - backend/API: `B`, `BE`, `back`, `backend`, `api`, `бэк`, `бек`, `бэкенд`;
  - frontend: `F`, `FE`, `front`, `frontend`, `фронт`, `фронтенд`, `фронтендер`;
  - QA: `Q`, `QA`, `test`, `testing`, `тест`, `тестирование`, `тестировщик`.
- Use `TBD_A`, `TBD_B`, `TBD_F`, `TBD_Q` for role-known but unassigned resources.
- The actual-progress generator normalizes known aliases on render; prefer canonical names in markdown to avoid review noise.

## Actual-progress mapping

Store story/task links in markdown, not as visual PlantUML dependencies.

- Use `features/<feature>/planning/actualization.md` for story-to-task mapping.
- Use `slices/*/execution/tasks.md` as source of truth for execution data.
- Many-to-many mapping is valid: one task may replace multiple stories, and one story may be replaced by multiple tasks.
- If the user says "replace story X by tasks A/B", update `actualization.md` and the tasks' `Related Stories`.
- If mapping is obvious from semantics, role and naming, use `mapping_mode = inferred`; if the user stated it explicitly, use `explicit`.
- Story progress is calculated from linked execution tasks, weighted by estimate.
- Story finish is the latest finish of linked replacement tasks; if a story has no replacement tasks, keep its commander baseline start unless `Depends On` says otherwise.
- Render a real task once even when it maps to multiple stories.

## Requirements rules

- Requirements are living markdown artifacts until release fixation.
- Write requirements by the project-local template in `.workflow/templates/requirements/`, not freeform.
- Start from `features/<feature>/requirements.md` as the primary feature-level requirement page and only place where feature requirements are authored from scratch.
- Build that page by the selected project-local requirements format:
  - new readable format: `.workflow/templates/requirements/feature-requirements.readable.template.md` plus `*.readable.template.md` slice/FE/BE packs;
  - old detailed format: `.workflow/templates/requirements/feature-requirements.template.md` plus the original slice/FE/BE templates.
- If the user names the format, obey it. If the feature already exists and the user does not name a format, preserve the current feature format. For a new feature without an explicit choice, use the new readable format.
- Do not mix new and old requirement formats inside one feature unless the user explicitly asks for a migration or comparison.
- Requirement diagrams must be PlantUML; do not introduce Mermaid blocks.
- Derive slice cards and FE/BE detail packs from the corresponding sections of the root feature requirements.
- If a slice artifact exposes a missing rule or contradiction, update `features/<feature>/requirements.md` first and only then re-derive the slice artifact.
- Keep business requirements, system requirements, acceptance criteria, API contracts and examples traceable to source materials.

## Fast consistency sweep for requirement edits

When a requirement change replaces one variant with another, remove stale tails in the same turn instead of leaving conflicting old wording behind.

Use a two-speed approach:

- `quick local sweep` is the default for minor edits confined to one feature or one slice;
- `full sweep` is required only when the change is clearly `cross-feature` or `domain-wide`.

Quick local sweep order:

1. update `features/<feature>/requirements.md`;
2. update the derived slice cards and FE/BE detail packs that repeat the changed rule;
3. update `features/<feature>/domain-impact.md` and `.workflow/consistency-backlog.md` if the change affects consistency tracking;
4. run a targeted text search, or equivalent local find-in-files sweep, across the current feature and any explicitly affected artifacts for superseded terms;
   if available, use `.workflow/tools/find-stale-terms.py` as the fast default helper;
5. specifically check for superseded:
   - old endpoint names;
   - old field names;
   - old role names;
   - old status values;
   - old UX labels or option names;
   - old Decision IDs or replaced contract filenames.

Do not answer a minor local edit with a whole-repo reread or a broad manual audit unless the user asked for it or the evidence shows wider drift.

## Prototype rules

- Default prototype stack: single-file `prototype.html`, React + MUI via CDN, no build step.
- Use only MUI components unless a project override says otherwise.
- Do not generate a prototype immediately after entering prototype mode; inspect existing prototypes and visual references first.
- Clarify with the user which prototype, screenshot, page or other artifact is the visual base when the basis is not already explicit.
- First work on one common root prototype in `features/<feature>/prototype.html` and `features/<feature>/prototype-notes.md`.
- The common root prototype must be a user-facing clickable prototype for the whole feature as the user will see it; do not put frontend handoff comments, API notes or developer explanations inside that HTML.
- Before touching any `features/<feature>/slices/*/delivery-prototype/*`, verify in `features/<feature>/prototype-notes.md` that both status lines are explicitly set to `да` for user confirmation and permission to proceed.
- If those confirmations are missing, stop and report that slice prototype generation is blocked until the root prototype is approved.
- Delivery prototypes are the only place for schematic frontend-facing explanations and must be derived from the confirmed root prototype plus current root requirements.
- Never fall back to editing an existing slice prototype just because `delivery-prototype` mode is active.


## Consistency propagation rules

When changing requirements, domain rules, lifecycle states, roles, API semantics, data model, or shared UI behavior, always perform impact detection in the same turn.

Minimum required steps:
- update or create `features/<feature>/domain-impact.md`;
- assign a stable `Decision ID` for accepted or likely-to-be-accepted decisions;
- classify impact as `local`, `cross-feature`, or `domain-wide`;
- list affected requirements;
- list affected baseline artifacts;
- list affected prototypes even if they will be updated later;
- update `.workflow/consistency-backlog.md` for any impact not propagated immediately.

The agent that edits local requirements performs first-pass impact detection. The main agent confirms and normalizes impact during consistency sweep. Release-finalization performs the final consistency gate before baseline promotion.

Shared requirements and canonical baseline updates must be integrated by the main agent, not blindly by parallel subagents.

## Prototype consistency rules

Prototype updates are optional unless the prototype is an active scope-demo or delivery-handoff artifact. Still, affected prototypes must be listed in `domain-impact.md` and/or `.workflow/consistency-backlog.md` so the user can later say "актуализируй прототипы" and the agent has a concrete target list.

Use prototype sync statuses:
- `must-update-now`;
- `defer-ok`;
- `no-update-needed`;
- `obsolete`.

## Rollback consistency rules

Rollback before release:
- mark the decision as `reverted-before-release`;
- mark related consistency items as `cancelled`;
- revert already-propagated living requirements if needed;
- do not change baseline unless the decision was already promoted.

Rollback after release:
- do not silently edit history;
- create a new rollback/change feature or release item;
- reference the original `Decision ID`;
- promote the rollback through `releases/` into a new `baseline/current` version.

Partial rollback:
- keep consistency backlog items open as `rollback-propagation-required` until affected requirements, baseline files and prototypes are reconciled.

## Safety and validation

- Never modify copied legacy/original source folders unless the user explicitly asks. For `changesWork`, read or copy only.
- Preserve user edits; do not revert unrelated changes.
- In a standalone project workspace, prefer project-local tools under `.workflow/tools/`.
- After planning/execution gantt edits, run `.workflow/tools/sync-quarter-gantt.py <project>/planning/<quarter>/gantt` when available.
- After structural edits, run `.workflow/tools/validate-structure.py <project>` and `.workflow/tools/validate-links.py <project>` when available.
- If working from the harness repo instead of a standalone project, the equivalent scripts may also exist under `scripts/`.
- If validation fails, fix the cause or report the exact residual issue.

## Baseline and release rules

- Keep the domain backbone in `baseline/current/domain/`, not only in raw source folders.
- Treat `context/source-materials/` and imported legacy folders as raw evidence, not as the canonical deployed state.
- Feature work describes deltas against `baseline/current/`; use `features/<feature>/domain-impact.md` for DDD impact.
- When a change is deployed, collect final requirements under `releases/<quarter>/<release-id>/` before promoting them.
- Promotion means:
  - update `baseline/current/`;
  - copy the previous baseline into `baseline/versions/<version>/`;
  - record the promoted version in `baseline/current/VERSION.md`;
  - record the source release in `releases/<quarter>/<release-id>/promoted-baseline-version.md`.

## Delegation rules

- Treat delegation as optional acceleration, not as a required capability.
- If subagents exist, use them only for bounded, non-overlapping tasks.
- The main agent remains responsible for semantic consistency of baseline, releases, and plan-vs-fact mapping.
- Never delegate final promotion decisions blindly.
- When delegating edits, assign explicit file ownership and require a returned changed-file list.

## Skills rules

- Skills are optional reusable behaviors, not a substitute for the project contract.
- Use a skill only if it clearly matches the current mode and improves repeatability.
- A skill must not bypass mode boundaries or mutate canonical baseline files outside release-finalization.
- When a platform has no native skills, follow the same rules through prompts/templates instead.

## Tool discipline

- Prefer markdown source-of-truth files over generated representations.
- Use PlantUML as a rendering target, not as the semantic store for mapping.
- Keep raw evidence in `context/source-materials/`.
- Prefer small, reviewable edits over broad rewrites.
