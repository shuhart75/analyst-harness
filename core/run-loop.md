# Run Loop Contract

Workflow modes define which source-of-truth artifacts may be changed. Run kinds define how one bounded unit of work is executed and verified.

## Shared Loop

Every run follows this control cycle:

1. orient from a small work packet;
2. plan the next bounded action;
3. execute one action;
4. run deterministic verification;
5. review the result independently from generation;
6. checkpoint evidence and unresolved questions;
7. continue, complete, or escalate.

A failed check does not advance the run. Repeated failure reaches the configured iteration limit and changes the run to `escalated`.

## Run Kinds

- `planning`: intake, delta, role stories, estimates, dependencies, capacity schedule, review, approval.
- `requirements`: root requirements, slices, detailed packs, feature-level developer task packs, cross-feature impact, task candidates, tail cleanup.
- `implementation`: code research, implementation plan, one small change, deterministic checks, review.
- `qa`: coverage, test design, execution, failure classification, routing gaps to their owner.

## Planning Invariants

- A feature is the quarter-level user or system outcome.
- A feature has at most one planning story per role: `AN`, `BE`, `FE`, `QA`.
- Missing role work means the corresponding story is absent.
- Approved quarter and commander plans are immutable baselines.
- Later scope is represented by task candidates and actual tasks in actual-progress, never by rewriting the approved plan.
- Default efficiency factors are `AN=0.80`, `BE=0.70`, `FE=0.65`, `QA=0.80`.
- FE starts no earlier than three open days after BE starts. If BE is absent, FE starts after AN or at the first available planning window when AN is also absent.
- Risk buffer is at least 20 percent. It changes commander-plan dates without being rendered as a separate management-facing bar.
- Priority is top-to-bottom. Idle roles may pipeline into the next feature, but lower-priority work must not delay newly available higher-priority work.
- Planning maximizes resource use without exceeding 100 percent.

## Requirement Impact Invariants

- Cross-feature work caused by the current feature is part of the initiating feature scope and HLE.
- Current requirements contain a dedicated `Доработки затронутых функциональностей` section.
- Every impact row is covered by requirements, task candidates, and checks or explicitly marked `not applicable` with a reason.
- Local stale tails block completion. Cross-mode propagation may be deferred only through a concrete consistency backlog record.

## Task Candidate Invariants

- Task candidates are generated while detailed requirements are prepared. The preferred handoff form is `features/<feature>/tasks/index.md` plus one file per task in `features/<feature>/tasks/`.
- Each task has one role and one independently committable technical result.
- Each task file is a self-contained development packet and the primary input for the implementation plan. Links to requirements and slices are traceability links, not instructions to go elsewhere for missing details.
- Target size for `BE`, `FE`, and `QA` is 1-3 person-days.
- Maximum size is 5 days for BE and 10 days for FE or QA. AN has no target or maximum.
- Candidates become actual tasks only after confirmation. Actual-progress uses one person per task.
- Slices remain useful for analytical completeness and prototypes, but task candidates do not have to be stored inside a slice.
- Creating feature-level development task files does not update planning baselines or actual-progress until the user asks to materialize them as execution tasks.
