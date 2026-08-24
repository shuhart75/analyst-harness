# Harness Rules

This repository is the root of a configurable analyst workspace. The harness remains here; analytical data and optional code live in independent sibling Git repositories.

## Communication language

- Communicate with the analyst in Russian, including progress updates, questions, status reports and final answers. Use English only for exact code, paths, identifiers, fixed product names and necessary special terms, or when the analyst explicitly requests another language.

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

- The `analyst-harness` repository is `HARNESS_ROOT`. Resolve the repository assigned role `analytics` as `PROJECT_ROOT` with `python3 scripts/workspace.py project-root`; do not assume a fixed directory name or derive it from the current directory.
- Resolve every relative harness path and command in this file against `HARNESS_ROOT`. When launched from `PROJECT_ROOT`, use the absolute `HARNESS_ROOT` written in the local entry point; never create replacement `scripts/`, `core/`, `modes/` or `templates/` under `PROJECT_ROOT`.
- Change requirements, plans, exchange revisions and factual progress only under `PROJECT_ROOT`.
- The tracked analytics tree must not contain an embedded `.workflow`, `.vscode`, or harness copy of `AGENTS.md`. A generated local `AGENTS.md` with marker `analyst-harness-local-entrypoint:v1` is allowed, ignored by Git, and must not be committed.
- Never stage local tool settings with `git add -A`, `git add .`, or another broad command. `.codex`, `.gigacode`, `.gigaide`, `.idea`, `GIGACODE.md`, `*.iml` and `*.orig` are local-only and must not be committed.
- Keep contracts, modes, scripts, templates and local run state in this harness root.
- Keep incoming reverse-patch pairs under the ignored `HARNESS_ROOT/reverse-patch-inbox/` and application receipts under the ignored `HARNESS_ROOT/reverse-patch-receipts/`; never commit either directory.
- Treat the optional code repository as strictly read-only except for registered operations: initial clone or creation, `git pull --ff-only` through `workspace.py update-code`, and publication through `requirements-exchange.py prepare`. Publication uses an isolated temporary clone, may commit and push only an existing root `requirements-exchange/**`, and must leave the ordinary code clone unchanged. It falls back to `PROJECT_ROOT/requirements-exchange/` when code is absent, the root catalog is absent, or read/push access fails. Do not otherwise change files, index, branch, `HEAD`, remotes, configuration or generated artifacts.
- If code is not configured, continue analytical work, state assumptions requiring receiver-side verification and use the reserve exchange catalog in role `analytics`.

## Code update commands

- `обнови код`, `обнови coda`, `обнови репу с кодом`, `обнови кодовый репозиторий`: run only `python3 scripts/workspace.py update-code`. This authorizes exactly one guarded `git pull --ff-only` for a configured cloned code repository, not arbitrary code changes.

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
11. `core/reverse-patch.md` before accepting a reverse patch
12. `core/run-loop.md`
13. `.workspace-state/run-state/session-brief.md` when present
14. `.workspace-state/active-mode.md`
15. `modes/<active-mode>.md`
16. `PROJECT_ROOT/README.md`
17. `PROJECT_ROOT/planning/team.md` before planning resources
18. relevant `PROJECT_ROOT/context/project-rules/*.md`

## Mode boundary

- Treat the active mode as a hard write boundary.
- Switch mode before changing artifacts owned by another mode, or ask the user to confirm the switch.
- Approved quarter and commander plans are immutable. Later work belongs to task candidates and actual-progress.

## Requirements

- Author requirements in Russian. Keep English only for exact code, paths, API and database identifiers, enum values, formats, fixed product names, and necessary technical terms.
- Root requirements are authored. During ordinary work, change only `PROJECT_ROOT/features/<feature>/requirements.md`; do not create slices, contour detail packs, preliminary developer tasks or exchange revisions.
- Before editing an existing feature, run `requirementsctl.py status`. If it reports an unrecorded divergence from the last published revision, do not guess its origin: ask whether it came from analyst initiative or a registered developer result and record that answer first.
- After every root requirement change, record its origin with `scripts/requirementsctl.py record-change`: `analyst` for an analyst-initiated change or `developer-result` with the stable `return_id` for accepted developer feedback.
- A `developer-result` change never creates or offers an exchange revision. An analyst-initiated change after an existing publication may produce one offer to prepare a new revision. Record the offer before asking; if declined, persist the refusal and do not ask again until an explicit preparation command.
- New root documents follow the sequential human-readable contract in `core/requirements-profile.md`; the ISO-shaped format is no longer used.
- Detect impact on neighboring features, include required neighboring work in the current requirements, and record deferred propagation in `planning/consistency-backlog.md` inside the analytical project.
- Never invent a business rule from code. Code observations are commit-bound technical evidence.
- Only the user-owner may approve requirements or plans.

## Developer handoff

- `сформируй пакет для разработки`, `отправь требования в разработку`, `передай требования разработчикам`, `передай разрабам`, `отдай требования разрабам`, `отправь разрабам`, `отдаём в разработку` and `передаём в разработку` are exact delivery synonyms.
- Treat each delivery synonym as one complete action: validate requirements, repair only meaning-preserving issues, ask one semantic question at a time, then run `requirements-exchange.py prepare` and publish directly to `sent` when all checks pass.
- Send only one immutable root `requirements.md` plus `manifest.json`. Do not create slices, contour packs or analyst-authored developer tasks.
- Developers return their already agreed decomposition in `returns/tasks.md`, per-task factual results in `returns/tasks/<task-id>.md`, and final `REQ-*` coverage in `returns/summary.md`. Analyst review never gates development.
- Preserve every sent input revision and its returns as immutable history.
- Always report the actual destination: remote code branch and repository path, or the absolute reserve path in role `analytics`, plus the revision number.
- Never create a ZIP unless the user explicitly requests it. A requested transport ZIP belongs only in `~/Downloads`, never in a repository.

## Code inspection

- Resolve the optional code repository through `.workspace-state/code-repos.json`; never require paths in routine user prompts.
- Inspect one contour at a time. Read local instructions, locate exact identifiers, then open only matched modules and nearby tests or contracts.
- Record branch, commit and worktree state before reading and verify unchanged state afterward.
- Do not fetch, pull, switch branches, build, format, generate, install dependencies, edit, commit, push, or run any command that can change the code repository during analytical inspection. Protected pull and isolated exchange publication are separate registered operations.

## Reverse patch reception

- `прими изменения из documents`, `примени обратную заплату`, `влей обратный дифф`, `влей изменения из documents` and close equivalents mean the complete guarded workflow in `core/reverse-patch.md`.
- Run `reverse_patch.py discover`, then `inspect`, then `apply`. Do not ask the user for a path. If several valid pairs exist, ask only which `artifact_id` to use; never choose automatically.
- `inspect` must independently validate patch applicability, whitespace rules and exact target-tree reproduction in a temporary index. A failed inspection is final for that immutable pair: do not run `apply`, edit the pair or touch the project worktree; request a newly generated pair.
- The command authorizes one protected pull of the configured analytical repository, one integration commit and a normal push to `origin/main`. It does not authorize reset, rebase, force push, broad staging or editing the patch.
- Report the final commit and local receipt. A failed push leaves a `committed-not-pushed` receipt so the same commit can be sent on the next run.

## Commands and validation

- Interpret short Russian commands through `templates/workflow/command-catalog.template.md` and `templates/workflow/command-cheatsheet.template.md`.
- Run `python3 scripts/harnessctl.py session-brief "$PROJECT_ROOT"` for progressive context disclosure.
- Run `python3 scripts/harnessctl.py doctor "$PROJECT_ROOT"` before broad workflow changes.
- Run `python3 scripts/validate-language.py "$PROJECT_ROOT"` after changing requirements.
- Run `python3 scripts/validate-requirements-profile.py "$PROJECT_ROOT"` for changed profiled root documents.
- Preserve unrelated user changes and report any validation failure that cannot be resolved within the requested scope.
