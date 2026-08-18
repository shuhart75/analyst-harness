# Code Inspection Policy

This policy governs read-only use of a locally cloned code repository by analysts and their LLM tools.

## Repository layout

The harness repository is the local working area. It contains one analytical repository and, when configured, one independent code repository:

```text
<workspace>/
├── analyst-harness/
├── .analyst-workspace.json
├── analyst-workspace.code-workspace
├── analytical-project/
└── code/                         # optional
```

The directory names are configurable during first launch. The analytical repository remains the source of requirements and planning. The optional code repository remains independent and read-only during analytical work. Do not merge them, create a submodule, or place a symlink to code inside the analytical repository.

The common parent gives the LLM filesystem access to both repositories. It does not authorize whole-repository reading and does not place all code into model context.

## Resolution and setup

The first-launch choices are stored locally in `.analyst-workspace.json`. `scripts/workspace.py bootstrap` prepares the selected repositories and writes the effective code location and contours to the analytical project's `.workflow/code-repos.json`.

Resolution order:

1. environment variable declared by the repository entry, normally `ANALYST_CODE_REPO`;
2. configured path relative to the analytical repository.

The harness must not store analyst-machine absolute paths in committed project files.

`scripts/workspace.py` creates `analyst-workspace.code-workspace` at the harness root. `code-inspect.py setup` can regenerate a minimal workspace when the repositories are already prepared manually.

## Read-only contract

During analyst planning and requirements work, the configured code repository is read-only.

Before inspection:

- resolve and validate the registered repository;
- record branch, full commit, origin, contour and worktree state;
- require a clean worktree for evidence used in requirements;
- read the selected contour's own agent or SDD instructions.

After inspection, compare branch, commit and worktree entries with the initial snapshot. Any change blocks completion until it is understood and removed by the repository owner.

Do not fetch, pull, switch branches, build, generate, format, install dependencies, run migrations, edit code or execute commands that may create files unless the user explicitly requests a separate code operation.

This is a workflow guard, not an operating-system sandbox. Use a client-provided read-only mount for the code root when available, but still perform the before/after verification.

## Bounded discovery

Code inspection is a targeted research action, not a repository audit.

1. Start from the feature question and exact identifiers already present in requirements or baseline.
2. Select one contour registered in `.workflow/code-repos.json`.
3. Read local instructions for that contour.
4. Use bounded filename/content search to locate exact routes, fields, statuses, tables, classes or components.
5. Open only matched modules, adjacent tests and necessary contracts or migrations.
6. Inspect the second contour in a separate pass only when a concrete dependency is found.
7. Stop when the question has sufficient evidence; do not broaden the search without a new question.

The public user does not need to provide paths. `code-inspect.py locate` returns a capped list of repository-relative matches and the exact inspected commit.

## Automatic triggers

The LLM may inspect code without an extra confirmation when the action is read-only and current implementation is needed to:

- answer an explicit request such as `сходи в код` or `проверь по коду`;
- establish current API, data, status, role or validation behavior;
- check whether an expected capability already exists;
- identify affected neighboring code before writing requirements;
- resolve a factual mismatch between `baseline/current/`, requirements and implementation;
- refresh previously recorded code evidence after the configured code commit changes.

Do not inspect code merely to derive a business decision that the code does not own. Ask the analyst when evidence leaves a semantic choice.

## Evidence and authority

For an ad hoc answer, report the inspected commit and relevant repository-relative paths without creating project files.

When code findings affect requirements, use `features/<feature>/.research/code-evidence.yaml`. Record:

- repository, branch, full commit and clean worktree state;
- one contour and one bounded question;
- facts, inferences, assumptions and open questions separately;
- relative paths, symbols and short observations without copying source code;
- related requirement identifiers and transfer destination.

Code evidence is auxiliary and commit-bound. Accepted findings must be transferred into root requirements, derived slice packs, `domain-impact.md` or the consistency backlog. Do not update `baseline/current/` from code research outside the existing release-finalization rules.

## Two-stage reconciliation

Analyst-side inspection improves requirements against a recorded local code revision. It does not replace developer-side reconciliation.

Before implementation, the receiving SDD repeats a targeted comparison against its current branch because the code may be newer, differently configured or already changed. Developer findings and actual delivery are returned through the existing decomposition and receipt lifecycle.
