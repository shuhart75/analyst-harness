# Entity Model

## Baseline snapshot

Canonical deployed-system description.

Contains:
- domain model
- canonical requirements
- API contracts
- UI structure notes
- data model notes
- decisions and baseline version metadata

## Feature

Main knowledge container for a business change.

Contains:
- planning artifacts
- slice definitions
- requirements
- prototypes
- execution tasks
- domain impact note

## Planning story

Used for:
- scope shaping
- HLE discussion
- analyst anchor estimate
- team estimate
- agreed estimate

Planning stories do not need to match implementation tasks 1:1.

Actualization states:
- `virtual`: the story is still the current execution unit.
- `mixed`: part of the story is covered by real implementation tasks, with a residual virtual scope still visible.
- `materialized`: the story is fully covered by real implementation tasks.
- `done`: the story is complete.

Mapping fields:
- `replaced_by`: implementation task ids that replace the planning story.
- `mapping_mode`: `explicit` when the user stated the replacement, `inferred` when LLM mapped it by feature/slice/role/summary.
- `residual_virtual_tasks`: virtual execution items that remain visible on actual-progress.

## Slice

A thematic subdivision of a feature.

A slice may contain:
- FE requirements
- BE requirements
- delivery prototype
- implementation tasks

## Implementation task

Execution tracking artifact with fields such as:
- Jira key
- summary
- kind: `real` or `virtual`
- estimate
- executor
- planned dates
- actual dates
- status
- progress %
- related/replaced planning stories
- optional description

## Domain impact note

Feature-local DDD delta against the current baseline.

Contains:
- changed bounded contexts
- changed aggregates/entities/value objects
- changed business rules and invariants
- lifecycle impact
- promotion targets into the next baseline

## Release package

Finalized delivery snapshot for a concrete release.

Contains:
- final requirements
- final domain delta
- final UI/API/data deltas
- promotion checklist
- promoted baseline version note
