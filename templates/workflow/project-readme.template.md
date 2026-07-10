# Project Knowledge Base

This project uses `analyst-harness` for planning, requirements, prototypes, implementation handoff, QA, execution tracking, and release finalization.

## Start

1. Read `AGENTS.md`.
2. Run `python .workflow/tools/harnessctl.py session-brief .`.
3. Run `python .workflow/tools/harnessctl.py doctor .` before broad workflow changes.
4. Use the role-oriented commands from `.workflow/command-cheatsheet.md`.

## Sources Of Truth

- `baseline/current/` — deployed current state.
- `planning/` — intake, immutable approved plans, and plan retrospectives.
- `features/` — feature deltas, requirements, slices, task candidates, and execution facts.
- `releases/` — delivered packages before baseline promotion.

## Planning

A feature is the quarter-level outcome. It has at most one planning story per role: `AN`, `BE`, `FE`, `QA`. Approved quarter and commander plans are immutable; later scope appears in actual-progress.

## Validation

```bash
python .workflow/tools/harnessctl.py doctor .
```
