# Code Inspection Policy

This policy governs read-only use of a locally cloned code repository by analysts and their LLM tools.

## Repository layout

The `analyst-harness` clone is `HARNESS_ROOT`. It contains role `analytics` and may contain an independent role `code`; their directory names and remote addresses come from the saved first-launch configuration.

```text
HARNESS_ROOT/
├── AGENTS.md
├── analyst-workspace.code-workspace
├── <analytics>/                  # PROJECT_ROOT
└── <code>/                       # optional, read-only for inspection
```

Role `analytics` remains the requirements and planning repository. Role `code` remains an independent optional code repository. Do not create submodules or symlinks between them.

The common workspace gives the LLM filesystem access to the registered repositories. It does not authorize whole-repository reading and does not place all code into model context.

## Resolution and setup

Repository identity, accepted remotes, relative location and contours are stored in `.workspace-state/code-repos.json`. The committed template has no product-specific address.

Resolution order:

1. environment variable declared by the repository entry, normally `ANALYST_CODE_REPO`;
2. path relative to `PROJECT_ROOT` from the saved workspace configuration.

The harness must not store analyst-machine absolute paths in committed project files.

`python3 scripts/workspace.py bootstrap` prepares the configured repositories and `analyst-workspace.code-workspace`. Do not use `code-inspect.py setup` to replace the root `AGENTS.md`; the root contract belongs to this harness.

If role `code` is skipped, code inspection is unavailable but all analytical work continues. Reconfiguration is an explicit user action; do not search for another clone or invent a path.

## Read-only contract

During analyst planning and requirements research, role `code` is strictly read-only. The only path exception is `requirements-exchange/**`, and it is usable only by the explicit protected transfer operation from `requirements-exchange.py` when the root catalog was created in advance by developers. A conversational user request does not extend it.

Before inspection:

- resolve and validate the registered repository;
- record branch, full commit, origin, contour, repository configuration and worktree state;
- require a clean worktree for evidence used in requirements;
- read the selected contour's own agent or SDD instructions.

After inspection, compare branch, commit, repository configuration and worktree entries with the initial snapshot. Any change blocks completion until it is handled by the code-repository owner. The analyst LLM must not repair, reset or clean it.

Do not fetch, pull, switch branches, build, generate, format, install dependencies, run migrations, edit code or execute commands that may create files during inspection. Protected `git pull --ff-only` is a separate registered workspace operation performed only through `workspace.py update-code` before a new inspection snapshot. Transfer through `requirements-exchange.py` is also separate from inspection and must not leave changes outside its registered path.

This is a workflow guard, not an operating-system sandbox. Use a client-provided read-only mount for role `code` when available, but still perform the before/after verification.

## Bounded discovery

Code inspection is a targeted research action, not a repository audit.

1. Start from the feature question and exact identifiers already present in requirements or baseline.
2. Select one contour, `backend` or `frontend`.
3. Read local instructions for that contour.
4. Use bounded filename/content search to locate exact routes, fields, statuses, tables, classes or components.
5. Open only matched modules, adjacent tests and necessary contracts or migrations.
6. Inspect the second contour in a separate pass only when a concrete dependency is found.
7. Stop when the question has sufficient evidence; do not broaden the search without a new question.

The public user does not need to provide paths. `code-inspect.py locate` searches only files tracked by the inspected Git commit and returns a capped list of repository-relative matches and the exact inspected commit. It does not require a separate content-search utility.

## Automatic triggers

The LLM may inspect code without an extra confirmation when the action is read-only and current implementation is needed to:

- answer an explicit request such as `сходи в код` or `проверь по коду`;
- establish current API, data, status, role or validation behavior;
- check whether an expected capability already exists;
- identify affected neighboring code before writing requirements;
- resolve a factual mismatch between `baseline/current/`, requirements and implementation;
- refresh previously recorded code evidence after the local role `code` commit changes.

Do not inspect code merely to derive a business decision that the code does not own. Ask the analyst when evidence leaves a semantic choice.

## Evidence and authority

For an ad hoc answer, report the inspected commit and relevant repository-relative paths without creating project files.

When code findings affect requirements, use `features/<feature>/.research/code-evidence.yaml`. Record:

- repository, branch, full commit and clean worktree state;
- one contour and one bounded question;
- facts, inferences, assumptions and open questions separately;
- relative paths, symbols and short observations without copying source code;
- related requirement identifiers and transfer destination.

Code evidence is auxiliary and commit-bound. During ordinary requirements work, transfer accepted requirement findings only into the root `requirements.md`; record deferred cross-feature propagation in the consistency backlog when necessary. Explicit developer transfer copies that root document and never creates another requirements representation. Do not update `baseline/current/` from code research outside the existing release-finalization rules.

## Two-stage reconciliation

Analyst-side inspection improves requirements against a recorded local code revision. It does not replace developer-side reconciliation.

Before implementation, the receiving SDD repeats a targeted comparison against its current branch because the code may be newer, differently configured or already changed. Developer findings and actual delivery are returned through `returns/tasks.md`, per-task results and the final summary of the active exchange revision.
