# Harness Rules

This repository defines a reusable workflow harness.

## Always read first

When working inside a project that uses this harness, read in this order:

1. `AGENTS.md`
2. `.workflow/llm-contract.md`
3. `.workflow/agent-delegation.md`
4. `.workflow/skills-policy.md`
5. `.workflow/tooling-policy.md`
6. `.workflow/active-mode.md`
7. `.workflow/modes/<active-mode>.md`
8. relevant files under `.workflow/overrides/`

## Primary workflow rule

Treat workflow mode as a hard guardrail.

- Do not change artifacts outside the active mode unless the user explicitly asks for a mode switch.
- If the requested change belongs to another mode, switch mode first or ask the user to confirm the switch.

## Canonical distinctions

Project-local intake templates live in `.workflow/templates/intake/`. Use them before scaffolding a new feature from an external folder or an unstructured initiative.

Project-local requirement templates live in `.workflow/templates/requirements/`. Use them as the active template source when writing or updating requirement packs.

- `planning story` is a planning and estimation unit only.
- `implementation task` is an execution tracking unit only.
- They are related, but they are not the same artifact.

## Feature-centered structure

Work should be grouped by:

- `feature`
- then `slice`
- then FE/BE requirement packs and execution artifacts

## Prototype stack

Use React + MUI without a build step unless a project override explicitly says otherwise.

## LLM contract

The project-local `.workflow/llm-contract.md` is the canonical CLI-neutral contract for Codex, Claude, Qwen, VSCodium agents, and similar assistants. Follow it before applying mode-specific rules.

## Companion policies

Project-local files `.workflow/agent-delegation.md`, `.workflow/skills-policy.md` and `.workflow/tooling-policy.md` define how an LLM should use delegation, reusable skills, and tools within this workflow.

## Consistency backlog

When a local change affects neighboring requirements, baseline artifacts, or prototypes and cannot be fully propagated immediately, record it in `.workflow/consistency-backlog.md`.

## Command catalog

Use `.workflow/command-catalog.md` to interpret short workflow commands like `делаем требования`, `обнови реальный прогресс`, `актуализируй прототипы`, or `промоуть в baseline`.

Use `.workflow/command-cheatsheet.md` as the preferred quick-reference list of ready-to-send Russian prompt phrasings.
