# Requirement Pack Templates

This directory contains the canonical requirement pack templates used by the harness.

## What lives here

- `feature-requirements.template.md` — старый подробный root feature requirement page для контроля и review
- `slice.template.md` — старая подробная semantic slice card derived from the root feature page
- `frontend.template.md` — старый подробный FE requirement pack
- `backend.template.md` — старый подробный BE requirement pack
- `feature-requirements.readable.template.md` — новый лёгкий корневой документ: бизнес-контекст, правила, схемы и контроль срезов
- `slice.readable.template.md` — новая короткая карточка среза
- `frontend.readable.template.md` — новый короткий FE-пакет с фокусом на UI, интеграцию и тестирование
- `backend.readable.template.md` — новый короткий BE-пакет с фокусом на API, данные, ошибки и тестирование

## Where the active project template lives

When a project is scaffolded, these templates are copied into:

- `.workflow/templates/requirements/feature-requirements.template.md`
- `.workflow/templates/requirements/slice.template.md`
- `.workflow/templates/requirements/frontend.template.md`
- `.workflow/templates/requirements/backend.template.md`
- `.workflow/templates/requirements/feature-requirements.readable.template.md`
- `.workflow/templates/requirements/slice.readable.template.md`
- `.workflow/templates/requirements/frontend.readable.template.md`
- `.workflow/templates/requirements/backend.readable.template.md`

Project-local copies are the templates that the LLM should follow when writing or updating requirements.

## Format selection

Требования можно генерировать в двух форматах.

| Формат | Когда использовать | Шаблоны |
|---|---|---|
| Новый лёгкий | пользователь просит `новый формат`, `лёгкий формат`, `как deployments`, `краткие срезы`; для новых фич по умолчанию, если формат не указан | `*.readable.template.md` |
| Старый подробный | пользователь просит `старый формат`, `подробный формат`, `как раньше`, Confluence-style структуру | `feature-requirements.template.md`, `slice.template.md`, `frontend.template.md`, `backend.template.md` |

Если обновляется уже существующая фича и пользователь не указал формат, сохраняй текущий формат этой фичи. Не смешивай форматы внутри одной фичи без явного запроса: root requirements, slice cards и FE/BE packs должны быть в одном выбранном стиле.

В новом лёгком формате:

- root requirements держит бизнес-контекст, длинные пояснения и спорные решения;
- slice cards короткие и содержат только границы, ссылки, проверяемые правила и фокус тестирования;
- каждый FE/BE-пакет содержит исчерпывающую информацию по своему срезу, включая чеклист тестирования;
- диаграммы пишутся только в PlantUML, Mermaid не используется.

## Writing rules

- Write requirement packs in Russian by default.
- Keep slugs, paths, ids and technical identifiers in English.
- Use the root feature page as the primary control document and single authored source.
- Derive slice cards and FE/BE packs from the corresponding sections of `features/<feature>/requirements.md`.
- Do not invent new slice scope independently from the root feature page.
- Treat requirements as living artifacts until release finalization.
- Keep business rules, system rules, acceptance criteria, API contracts and examples traceable to source materials.
- If a change affects neighboring features, baseline artifacts or prototypes, update `domain-impact.md` and `.workflow/consistency-backlog.md` in the same turn.

## Minimal workflow

1. Select the requirements format: new readable or old detailed.
2. Create or update `features/<feature>/requirements.md` by the selected root template.
3. Fix the explicit slice order and section boundaries there.
4. Create or update `slices/*/slice.md` as a decomposition map derived from the root document.
5. Fill `requirements/frontend.md` and/or `requirements/backend.md` as detail annexes for each slice section.
6. Link the relevant prototypes.
7. Register consistency impact in `features/<feature>/domain-impact.md`.

## Fast post-edit checklist

Use this after a requirement edit so the first pass already cleans up most tails.

1. Recheck the changed rule in the root feature document.
2. Recheck every slice artifact that repeats the same rule.
3. Search the current feature for superseded terms:
   - old endpoint names;
   - old field names;
   - old role names;
   - old status values;
   - old UX labels or option names;
   - old contract filenames or Decision IDs.
4. If a stale mention is outside the active edit scope, record it in `.workflow/consistency-backlog.md` instead of leaving it implicit.

Default to this feature-local sweep first. Expand further only when the change is clearly cross-feature or domain-wide.
