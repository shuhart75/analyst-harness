# analyst-harness

Editor-agnostic workflow harness for long-lived product knowledge: baseline domain model, quarter planning, requirements work, MUI prototypes, execution updates, and release finalization.

This repository is designed to work with Codex CLI, Claude Code, Qwen CLI, and similar LLM-driven terminal workflows. VSCodium support is provided as an adapter layer, not as the source of truth.

## Design goals

- Keep workflow rules in the repository, not in one IDE.
- Treat the project as a long-lived knowledge base, not a one-off task folder.
- Keep a canonical deployed baseline separate from planned or in-progress changes.
- Support planning, delivery, execution updates, and release finalization as different modes.
- Keep `planning story` separate from `implementation task`.
- Keep artifacts grouped by `feature` and then by `slice`.
- Use React + MUI prototypes with no build step so a single `prototype.html` can be opened locally or sent by email.

## Quick command entry

If you use the harness through an LLM, start here:

- `.workflow/command-cheatsheet.md` - ready-to-send Russian command phrasings
- `.workflow/command-catalog.md` - canonical interpretation rules and mode mapping
- `.workflow/templates/requirements/` - active project-local requirement templates

Minimal daily command set:

- `новая фича`
- `занимаемся планированием`
- `делаем требования`
- `делаем презентационный прототип`
- `делаем прототип для разработки`
- `обновляем прогресс`
- `финализируем релиз`

Typical usage:

```text
новая фича
Источник: `/path/to/folder`
Квартал: `2026-Q2`
```

```text
делаем требования
В папке `context/source-materials/change-requests/packages-filtering` лежат скрины и описание.
Нужно подготовить requirement pack по feature/slice, обновить domain-impact и перечислить затронутые прототипы.
```

## Core concepts

- `baseline/current` is the canonical current-state system description.
- `feature` is the main container for a change delta.
- `planning stories` drive quarter and commander plans.
- `planning/intake/*` captures feature preflight notes before scaffolding.
- `implementation tasks` drive actual progress.
- `requirement packs` live under `feature -> slice -> FE/BE`, using project-local templates from `.workflow/templates/requirements/`.
- `scope prototype` is a live demo prototype for shaping and HLE discussions.
- `delivery prototype` is a precise React + MUI prototype for handoff and developer alignment.
- `releases/*` store final delivered requirements before promotion into a new baseline.

## Modes

- `planning`
- `requirements`
- `scope-prototype`
- `delivery-prototype`
- `execution-update`
- `release-finalization`

Each working project should contain:

- `.workflow/llm-contract.md`
- `.workflow/agent-delegation.md`
- `.workflow/skills-policy.md`
- `.workflow/tooling-policy.md`
- `.workflow/tools/`
- `.workflow/active-mode.md`
- `.workflow/modes/*.md`
- `.workflow/templates/intake/`
- `.workflow/templates/requirements/`
- `.workflow/command-cheatsheet.md`
- `.workflow/overrides/*.md`
- `baseline/current/`
- `releases/`
- `planning/intake/`

The active mode defines what the assistant is allowed to change without an explicit mode switch.

## Repo layout

- `core/` - permanent workflow contracts, including the CLI-neutral LLM contract
- `modes/` - mode-specific rules
- `templates/` - markdown, baseline and release templates
- `scripts/` - scaffolding and validation helpers
- `adapters/cli/` - shell helpers for mode switching and session bootstrap
- `adapters/vscodium/` - VSCodium tasks, snippets, and suggested settings
- `examples/demo-project/` - small sample layout

## Quick start

1. Create a new project skeleton:

```bash
bash scripts/scaffold-project.sh /path/to/project
```

2. Switch mode in that project:

```bash
bash adapters/cli/switch-mode.sh /path/to/project planning
```

3. Start a session by telling the LLM where the project lives and which mode is active.

Project-local runtime helpers will be available under `.workflow/tools/`, so a standalone project can validate itself without depending on the harness repo being opened as the workspace root.

4. Add features and slices as needed:

```bash
bash scripts/scaffold-quarter.sh /path/to/project 2026-Q2
bash scripts/scaffold-feature.sh /path/to/project deployments
bash scripts/scaffold-slice.sh /path/to/project deployments form-editing
```

## Prototype standard

All prototypes use a single-file `prototype.html` based on:

- React 18 via CDN
- ReactDOM via CDN
- MUI via CDN
- Babel standalone

This keeps prototypes portable and easy to open with Live Preview, a browser, or email recipients.
