# Mode: execution-update

## Goal

Track real work after planning.

## Main artifacts

- `features/*/slices/*/execution/tasks.md`
- `features/*/slices/*/execution/tasks/*.md`
- `features/*/planning/actualization.md`
- `planning/*/gantt/actual-progress.puml`

## Allowed changes

- task status
- task kind and progress %
- executor
- planned dates
- actual dates
- description and notes
- mapping `planning story -> implementation task`
- actualization state: `virtual` / `mixed` / `materialized`
- milestones and factual notes in actual-progress gantt

## Forbidden without mode switch

- changing agreed planning estimates
- changing quarter or commander baseline gantt silently
