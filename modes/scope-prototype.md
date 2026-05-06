# Mode: scope-prototype

## Goal

Build or update the common feature-level live prototype that is used for scope discussion, customer alignment, and the future derivation of slice handoff prototypes.

## Main inputs

- `features/*/requirements.md`
- existing `features/*/prototype.html` and `features/*/prototype-notes.md` when they already exist
- existing prototypes of the same feature first
- current-system screenshots, requirements, design references and change-request materials

## Main outputs

- `features/*/prototype.html`
- `features/*/prototype-notes.md`
- optional legacy mirror: `features/*/planning/scope-prototype/*` only when the task explicitly asks to keep that folder in sync

## Required first actions

1. Look for existing prototypes of the same feature first.
2. Look for other plausible visual bases: screenshots, current-system pages, old prototypes, design references.
3. Clarify with the user which artifact should be the visual base when the basis is not already explicit.

## Rules

- Do not generate a new prototype immediately after the mode switch.
- First identify and agree the base reference for styles, colors, layout and component behavior.
- Work only on one common feature-level prototype in the root of the feature.
- This root prototype is a user-facing clickable prototype for the whole feature as the end user will see it.
- Do not put frontend handoff comments, implementation notes, API notes, or developer explanations inside the root `prototype.html`.
- Keep iterating only on that common prototype until the user explicitly confirms it is finished.
- Make it live, clickable and rich with fake data.
- Show ideal target state and MVP cut in the same prototype when useful.
- Optimize for discussion and agreement, not for frontend handoff precision.
- Update `features/<feature>/prototype-notes.md` on every iteration and keep the status fields truthful.

## Forbidden without mode switch

- editing `features/*/slices/*/delivery-prototype/*`
- generating slice-level handoff prototypes before the user confirms the common feature prototype is finished
- treating the first generated draft as frozen without explicit user confirmation
