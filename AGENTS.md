# Harness Rules

This repository is the root of a configurable analyst workspace. The harness remains here; analytical data and optional code live in independent sibling Git repositories.

## First launch

- If `.analyst-workspace.json` is absent, ask the user one question at a time:
  1. clone or create the analytical repository;
  2. if clone was selected, request its URL;
  3. clone, create, or skip the code repository;
  4. if clone was selected, request its URL.
- Use the default directories `analytical-project/` and `code/` unless the user explicitly chooses others.
- Save the answers with `python3 scripts/workspace.py configure ...`, then run `python3 scripts/workspace.py bootstrap`.
- If the configuration exists but the configured repository or workspace file is absent, run bootstrap without repeating questions.
- Never infer or insert a product-specific repository URL.

## Ownership boundaries

- Read the analytical root from `.analyst-workspace.json`; do not assume a fixed directory name in user interaction.
- Change requirements, plans, packages and factual progress only in the configured analytical repository.
- The analytical repository must not contain an embedded `.workflow`, `.vscode`, or root `AGENTS.md` harness copy.
- Keep contracts, modes, scripts, templates and local run state in this harness root.
- Treat the optional code repository as read-only. Its local push URL is disabled when it was cloned by the harness.
- If code is not configured, continue analytical work and state technical assumptions that require receiver-side verification.

## Always read first

1. `AGENTS.md`
2. `.analyst-workspace.json`
3. `core/llm-contract.md`
4. `core/requirements-profile.md` before authoring or substantially rewriting requirements
5. `core/agent-delegation.md`
6. `core/skills-policy.md`
7. `core/tooling-policy.md`
8. `core/context-policy.md`
9. `core/research-policy.md`
10. `core/code-inspection.md` when code evidence is needed
11. `core/run-loop.md`
12. `.workspace-state/run-state/session-brief.md` when present
13. `.workspace-state/active-mode.md`
14. `modes/<active-mode>.md`
15. `<analytical-project>/README.md`
16. `<analytical-project>/planning/team.md` before planning resources
17. relevant `<analytical-project>/context/project-rules/*.md`

## Mode boundary

- Treat the active mode as a hard write boundary.
- Switch mode before changing artifacts owned by another mode, or ask the user to confirm the switch.
- Approved quarter and commander plans are immutable. Later work belongs to task candidates and actual-progress.

## Requirements

- Author requirements in Russian. Keep English only for exact code, paths, API and database identifiers, enum values, formats, fixed product names, and necessary technical terms.
- Root requirements are authored. Slice cards and contour detail packs are derived and must be regenerated after semantic root changes.
- New root documents follow `core/requirements-profile.md`, an adaptation of ISO/IEC/IEEE 29148:2018.
- Detect impact on neighboring features, include required neighboring work in the current requirements, and record deferred propagation in `planning/consistency-backlog.md` inside the analytical project.
- Never invent a business rule from code. Code observations are commit-bound technical evidence.
- Only the user-owner may approve requirements or plans.

## Developer handoff

- Treat `сформируй пакет для разработки` and its documented synonyms as one complete action: validate requirements, repair only meaning-preserving issues, ask one semantic question at a time, and publish directly to `sent` when all checks pass.
- Send one feature package containing root requirements and slices. Do not pre-author the final Jira decomposition under `features/<feature>/tasks/`.
- Developers own confirmed `DEV-BE-*` and `DEV-FE-*` cards after inspecting their code and local SDD.
- A confirmed decomposition snapshot is returned in the background and does not block implementation.
- Keep input revisions, decomposition snapshots, implementation receipts, and slice test receipts independent and immutable where the contract requires it.
- Never create a ZIP unless the user explicitly requests it. A requested transport ZIP belongs only in `~/Downloads`, never in a repository.

## Code inspection

- Resolve the optional code repository through `.workspace-state/code-repos.json`; never require paths in routine user prompts.
- Inspect one contour at a time. Read local instructions, locate exact identifiers, then open only matched modules and nearby tests or contracts.
- Record branch, commit and worktree state before reading and verify unchanged state afterward.
- Do not fetch, pull, switch branches, build, format, generate, install dependencies, or run commands that can change the code repository during analytical inspection.

## Commands and validation

- Interpret short Russian commands through `templates/workflow/command-catalog.template.md` and `templates/workflow/command-cheatsheet.template.md`.
- Run `python3 scripts/harnessctl.py session-brief <analytical-project>` for progressive context disclosure.
- Run `python3 scripts/harnessctl.py doctor <analytical-project>` before broad workflow changes.
- Run `python3 scripts/validate-language.py <analytical-project>` after changing requirements.
- Run `python3 scripts/validate-requirements-profile.py <analytical-project>` for changed profiled root documents.
- Preserve unrelated user changes and report any validation failure that cannot be resolved within the requested scope.
