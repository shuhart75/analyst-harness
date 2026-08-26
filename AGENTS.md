# Harness Rules

This repository is the root of a configurable analyst workspace. The harness remains here; analytical data and optional code live in independent sibling Git repositories.

## Communication language

- Communicate with the analyst in Russian, including progress updates, questions, status reports and final answers. Use English only for exact code, paths, identifiers, fixed product names and necessary special terms, or when the analyst explicitly requests another language.

## Mandatory tracker stop gate

- Before any tracker MCP discovery, search, issue read, history read or delegation, run `python3 scripts/trackerctl.py config-status` as a standalone command. Do not pipe or filter it through `head`, `tail`, `grep`, `jq` or another command: the exit code is part of the guard contract.
- Exit code `3` with `must_stop: true` permits exactly one next action: ask the analyst the single returned `next_question`. Emit the exact `response_contract.text` and nothing else: no preface, explanation, examples, suggested answers or summary. Do not call MCP tools, search analytical files for tasks, create a task list, delegate work or present tracker facts until the answer is saved and the gate becomes ready.
- Commands that save one configuration answer return exit code `0` and another status payload. When that payload still has `must_stop: true`, ask only its `next_question`; do not bypass it with discovery or reading.
- Tracker MCP calls may start only after a ready status and successful `trackerctl.py begin` returning a `run_id`. The main agent performs all tracker reads itself; subagent delegation is forbidden for this workflow.
- After `begin`, persist every MCP result immediately through `snapshot-metadata`, `snapshot-issue`, `snapshot-history` and `snapshot-collection`; do not postpone normalization or hand-author the complete snapshot. Run `run-status --run-id <run_id>`, complete every reported gap, then run the exact `reconcile --run-id <run_id>` command. Direct MCP data is not a report.
- A tracker summary is allowed only after `trackerctl.py reconcile` returns `status: tracker-read-reconciled`, `workflow_complete: true` and `final_response_allowed: true` for that `run_id`. Any nonzero exit or `final_response_allowed: false` forbids a user-facing summary even when MCP data has already been read; perform only `allowed_next_action` and retry the guard.

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
5. `core/requirements-wording.md` before writing or checking requirement prose
6. `core/requirements-audit.md` before checking or delivering requirements
7. `core/agent-delegation.md`
8. `core/skills-policy.md`
9. `core/tooling-policy.md`
10. `core/context-policy.md`
11. `core/research-policy.md`
12. `core/code-inspection.md` when code evidence is needed
13. `core/tracker-reading.md` when the user asks to read or compare task trackers
14. `core/collaboration.md` before starting, saving, updating, submitting or finishing feature work
15. `core/reverse-patch.md` before accepting a reverse patch
16. `core/run-loop.md`
17. `.workspace-state/run-state/session-brief.md` when present
18. `.workspace-state/active-mode.md`
19. `modes/<active-mode>.md`
20. `PROJECT_ROOT/README.md`
21. `PROJECT_ROOT/planning/team.md` before planning resources
22. relevant `PROJECT_ROOT/context/project-rules/*.md`

## Mode boundary

- Treat the active mode as a hard write boundary.
- Switch mode before changing artifacts owned by another mode, or ask the user to confirm the switch.
- Approved quarter and commander plans are immutable. Later work belongs to task candidates and actual-progress.

## Requirements

- Author requirements in Russian. Keep English only for exact code, paths, API and database identifiers, enum values, formats, fixed product names, and necessary technical terms.
- Root requirements are authored. During ordinary work, change only `PROJECT_ROOT/features/<feature>/requirements.md`; do not create slices, contour detail packs, preliminary developer tasks or exchange revisions.
- On an explicit one-time migration from the superseded ISO-shaped document, rename the former root to `requirements_iso.md`, create the new root from the readable template, and then treat the archive as immutable history. Never send `requirements_iso.md` or use it as the authored source.
- Before editing an existing feature, run `requirementsctl.py status`. If it reports an unrecorded divergence from the last published revision, do not guess its origin: ask whether it came from analyst initiative or a registered developer result and record that answer first.
- After every root requirement change, record its origin with `scripts/requirementsctl.py record-change`: `analyst` for an analyst-initiated change or `developer-result` with the stable `return_id` for accepted developer feedback.
- A `developer-result` change never creates or offers an exchange revision. An analyst-initiated change after an existing publication may produce one offer to prepare a new revision. Record the offer before asking; if declined, persist the refusal and do not ask again until an explicit preparation command.
- New root documents follow the compact specification contract in `core/requirements-profile.md`; the ISO-shaped and former sequential profiles are no longer used for new delivery revisions.
- Compact `requirements.md` must not contain `Статус`. Use `requirements-state.json` for authoring and audit state and exchange `manifest.json` for delivery state.
- Requirement prose follows `core/requirements-wording.md`. Use explicit quantities and named referents; every scenario must identify a concrete state, event and observable result. Run `validate-requirements-wording.py` after substantive edits and before showing the document as checked.
- Do not reproduce the developer's technical `spec.md`. Write a business contract with stable `REQ-*` headings and nested Russian `Когда`/`Тогда` scenarios; the receiving SDD derives its own technical delta from it and the code.
- Detect impact on neighboring features, include required neighboring work in the current requirements, and record deferred propagation in `planning/consistency-backlog.md` inside the analytical project.
- Never invent a business rule from code. Code observations are commit-bound technical evidence.
- Only the user-owner may approve requirements or plans.

## Collaboration

- Multi-user feature branches are mandatory for requirements work. Missing `.workspace-state/collaboration.json` means migration is required; it never permits direct work in `PROJECT_ROOT/main`.
- `начинаю работу над фичей <feature>` and documented synonyms mean: run bootstrap, check `collaboration.py status`, migrate once when required, then run `collaboration.py start --feature <feature>` before reading or editing the feature requirements.
- `сохрани работу` and documented synonyms mean: review all changes, run applicable checks, then call `collaboration.py save` with every exact changed path and a semantic commit message. It pushes only the feature branch.
- Bare `обнови` or `синкани` while feature work is active means `collaboration.py update`. Outside active work the phrase is ambiguous and requires one question.
- `требования готовы к объединению` means validate, save, update, revalidate and call `collaboration.py submit`. It pushes the branch but does not create or accept a merge request.
- `запрос на слияние принят` means `collaboration.py finish`, which must prove that the submitted commit is contained in `origin/main` before returning to local `main`.
- Never work directly in `main`, rebase, reset, force push, use broad staging, or create delivery revisions from an unaccepted feature branch.

## Developer handoff

- `сформируй пакет для разработки`, `отправь требования в разработку`, `передай требования разработчикам`, `передай разрабам`, `отдай требования разрабам`, `отправь разрабам`, `отдаём в разработку` and `передаём в разработку` are exact delivery synonyms.
- Before beginning the audit, require `collaboration.py require-main-for-delivery --feature <feature>`. Delivery is allowed only from current `PROJECT_ROOT/main` after the feature branch has been accepted and the collaboration session has been finished.
- Treat each delivery synonym as a two-stage action. First run all three audit levels in `core/requirements-audit.md`: individual rules, cross-requirement system reasoning and delivery readiness. Repair only meaning-preserving issues, ask one semantic question at a time, recheck affected relations after each answer, then rerun all three levels over the complete document. Show the final audit report and request explicit confirmation. Do not create or publish a revision before that confirmation.
- Record the completed audit with `requirementsctl.py record-audit`. Only an analyst reply that explicitly confirms both the shown audit and transfer authorizes `requirementsctl.py confirm-audit`; silence, an earlier transfer command, or approval of the requirements document itself is not confirmation of the audit.
- After confirmation, publish the unchanged audited file directly to `sent`. If `requirements.md` changes at any point after the audit, repeat the audit and confirmation; `requirements-exchange.py prepare` enforces this checksum boundary.
- Send only one immutable root `requirements.md` plus `manifest.json`. Do not create slices, contour packs, analyst-authored developer tasks or local OpenSpec artifacts on behalf of developers.
- The receiver treats `requirements.md` as an upstream business contract, compares it with current code and creates its own local SDD artifacts separately for backend and frontend. Mixed backend/frontend tasks are forbidden; one `REQ-*` may map to multiple contour tasks.
- Developers return their already agreed decomposition in `returns/tasks.md`, per-task factual results in `returns/tasks/<task-id>.md`, and final `REQ-*` coverage in `returns/summary.md`. Analyst review never gates development.
- Preserve every sent input revision and its returns as immutable history.
- Always report the actual destination: remote code branch and repository path, or the absolute reserve path in role `analytics`, plus the revision number.
- Never create a ZIP unless the user explicitly requests it. A requested transport ZIP belongs only in `~/Downloads`, never in a repository.

## Code inspection

- Resolve the optional code repository through `.workspace-state/code-repos.json`; never require paths in routine user prompts.
- Inspect one contour at a time. Read local instructions, locate exact identifiers, then open only matched modules and nearby tests or contracts.
- Record branch, commit and worktree state before reading and verify unchanged state afterward.
- Do not fetch, pull, switch branches, build, format, generate, install dependencies, edit, commit, push, or run any command that can change the code repository during analytical inspection. Protected pull and isolated exchange publication are separate registered operations.

## Task tracker reading

- `прочитай задачи из трекеров`, `проверь задачи в трекерах`, `сверь SberTrek и Jira`, `покажи текущее состояние по трекерам` and close equivalents mean the read-only workflow in `core/tracker-reading.md`.
- Discover MCP tools by task-search, issue-read and history-read capabilities; never depend on a fixed MCP server name and never store MCP names or credentials in Git.
- Read SberTrek first as the primary source. Use Jira only to fill missing fields and merge history. A conflicting populated Jira field never silently replaces SberTrek.
- Treat epic and release as independent grouping dimensions. Never infer that an epic equals an analytical feature without an explicit mapping.
- Apply the handoff rule only to tracker types explicitly configured as development work items; this may include a tracker Story. An explicit excluded or completed status takes precedence. Otherwise infer development completion only from history proving the latest handoff from a mapped developer to a mapped non-developer.
- Starting from known task keys, record one analytical `seed_evidence` source per seed, then inspect the other tasks in each discovered epic as bounded candidates. A text-search hit is not a seed. Analyze candidate title and description; propose directly evidenced matches and ask about ambiguous matches. Report releases missing from actual-progress as proposals only.
- Run the exact `config-status -> begin -> reconcile` protocol from `core/tracker-reading.md`. Ask every returned configuration or participant question one at a time. Never continue after a guard error, mark a collection capability complete without calling it, or reconcile a default/empty configuration.
- Direct-read every declared counterpart key and record whether it was found. Preserve provider timestamps exactly. A search result alone does not prove complete history, epic, release or counterpart collection.
- Present counts and limitations directly from `trackerctl` output and `report.md`; never recount discrepancies manually. A non-empty `limitations` list must be visible to the analyst.
- The read command may write only ignored runtime artifacts under `.workspace-state/tracker-runs/`. It must not change trackers, `PROJECT_ROOT`, requirements, plans, actual-progress or Git state.

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
- Run `python3 scripts/validate-requirements-wording.py "$PROJECT_ROOT"` for changed compact requirements. A successful script result never replaces the isolated-reader review from `core/requirements-wording.md`.
- Preserve unrelated user changes and report any validation failure that cannot be resolved within the requested scope.
