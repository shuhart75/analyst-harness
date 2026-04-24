# Skills Policy

This harness is CLI-neutral, so "skills" may come from Codex, Claude, Qwen, or project-local prompting conventions.

## Principle

Use a skill only when it adds repeatable domain value or enforces a stable workflow pattern.

## Recommended skill categories

- `planning-analyst` — HLE decomposition, planning stories, estimates, gantt semantics.
- `requirements-analyst` — business/system requirements from baseline and source materials.
- `scope-prototyper` — planning-stage clickable prototype with fake data.
- `delivery-prototyper` — slice-level MUI handoff prototype.
- `execution-tracker` — implementation task updates and actual-progress mapping.
- `release-promoter` — final requirements, baseline promotion, release package assembly.
- `domain-curator` — baseline/current/domain maintenance and DDD normalization.

## Skill input discipline

A skill should explicitly state:
- which mode it assumes;
- which directories are canonical inputs;
- which files it is allowed to write;
- what validation is expected after completion.

## Skill anti-patterns

Do not create skills that:
- duplicate one-off commands with no reusable logic;
- bypass mode boundaries;
- assume one vendor-specific tool unless clearly marked;
- silently mutate canonical baseline files without release-finalization context.
