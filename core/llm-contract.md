# LLM Contract

This contract is CLI-neutral. It applies to Codex CLI, Claude Code, Qwen CLI, VSCodium agents, and other LLM assistants working in a project scaffolded with this harness.

## Session bootstrap

Before changing artifacts, read:

1. `AGENTS.md`
2. `.workflow/llm-contract.md`
3. `.workflow/agent-delegation.md`
4. `.workflow/skills-policy.md`
5. `.workflow/tooling-policy.md`
6. `.workflow/active-mode.md`
7. `.workflow/modes/<active-mode>.md`
8. relevant `.workflow/overrides/*.md`
9. `.workflow/templates/intake/` when the user brings a candidate new feature
10. `.workflow/templates/requirements/` when working in requirements mode
11. `.workflow/templates/prototypes/` when working in prototype modes
12. `baseline/current/` for the canonical deployed state when it exists
13. relevant `features/<feature>/feature.md`, root requirements, root prototype, slice artifacts, planning stories, execution tasks and gantt includes
14. relevant `releases/` artifacts when finalizing a delivered change

If the user points to a folder with current-system docs/screenshots/change requests, inspect that folder first and keep source references in the produced artifacts.


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
- Build that page by `.workflow/templates/requirements/feature-requirements.template.md`, preserving the Confluence-style structure used by the user template.
- Derive slice cards and FE/BE detail packs from the corresponding sections of the root feature requirements.
- If a slice artifact exposes a missing rule or contradiction, update `features/<feature>/requirements.md` first and only then re-derive the slice artifact.
- Keep business requirements, system requirements, acceptance criteria, API contracts and examples traceable to source materials.

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
