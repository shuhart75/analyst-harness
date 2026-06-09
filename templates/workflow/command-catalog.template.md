# Command Catalog

This file documents short natural-language commands that switch context or trigger recurring workflow actions.

## Interpretation rules

- Commands are intent shortcuts, not magic shell commands.
- If a command implies a mode switch, update `.workflow/active-mode.md` or explicitly state that the user should switch mode if the runtime cannot edit it.
- After a mode switch, read the target mode file before editing artifacts.
- If a command includes a folder/path, inspect that path before writing outputs.
- If a command causes cross-feature/domain impact, update `features/*/domain-impact.md` and `.workflow/consistency-backlog.md` as needed.
- For small requirement edits, prefer a quick feature-local tail cleanup over a whole-repo audit.
- If a command is ambiguous, make a reasonable assumption and state it briefly; ask only when the wrong assumption would create significant rework.

## Daily core command set

Use this as the preferred short set for everyday work. In VSCodium these commands are mirrored by prompt starters in `.vscode/workflow.code-snippets`.

## How to use these commands

- Commands are ordinary natural-language phrases. Write them directly to the LLM in chat, with no slash syntax.
- A command may be the whole message or the first line of a longer request.
- After the command, add concrete context: folders, feature ids, release ids, screenshots, dates, task ids, constraints.
- One message may contain one mode switch command plus the concrete work to do in that mode.
- If you switch mode implicitly, the LLM should first read the target mode rules, then update artifacts.
- In VSCodium, type a snippet prefix such as `wf-plan` or `wf-req`, press Tab/Enter, then fill placeholders and send the generated text to the LLM.

## Recommended command shape

Use a two-part pattern:

1. first line: short command from this catalog;
2. next lines: concrete task context and expected output.

Examples:

```text
новая фича
Источник: `/home/reutov/Documents/AI/simulations_AI_agent`
Квартал: `2026-Q2`
Нужно сделать intake: ничего не создавать, сначала отделить baseline от новой дельты.
```

```text
занимаемся планированием
В папке `context/source-materials/change-requests/mobile-scorecards` лежат скрины и описание.
Нужно разложить доработку на planning stories, дать HLE в человеко-днях с разрезом `AN / FE / BE / QA` и обновить quarter-plan/commander-plan.
```

```text
делаем требования
В папке `context/source-materials/change-requests/packages-filtering` лежат текущие требования и новые скрины.
Формат: новый лёгкий
Нужно подготовить `features/<feature>/requirements.md` по выбранному шаблону, зафиксировать там порядок и границы срезов, а потом разложить root document по detail packs, обновить domain-impact и перечислить затронутые прототипы.
```

```text
делаем презентационный прототип
Feature: `packages`
Материалы: `context/source-materials/change-requests/packages-filtering`
Сначала найди существующие прототипы и скриншоты этой feature, помоги выбрать базовый референс, и пока работай только с общим `features/packages/prototype.html`.
```

```text
общий прототип согласован
Feature: `packages`
Теперь возьми подтверждённый root prototype и требования из `features/packages/requirements.md`, разложи их на slice-level handoff prototypes для фронтендера.
```

```text
обновляем прогресс
RSCON-2445 завершена вчера, RSCON-2451 взял второй фронтендер позавчера.
Добавь milestone релиза на 2026-04-30, обнови actual-progress и Confluence-копию без include.
```

| Core command | Mode | Primary intent |
|---|---|---|
| `новая фича` | `planning` | Run feature intake/preflight before any scaffold step. |
| `занимаемся планированием` | `planning` | Switch into quarter planning and HLE mode. |
| `делаем требования` | `requirements` | Switch into living requirements mode and use the requested requirements format. |
| `делаем презентационный прототип` | `scope-prototype` | Switch into common feature prototype mode and choose the visual base before generating. |
| `делаем прототип для разработки` | `delivery-prototype` | Switch into slice handoff mode, but block any slice edits until the root feature prototype is explicitly approved. |
| `обновляем прогресс` | `execution-update` | Switch into implementation tracking mode. |
| `финализируем релиз` | `release-finalization` | Switch into release/baseline promotion mode. |
| `актуализируй требования` | `requirements` | Update requirements and propagate impact. |
| `проверь хвосты требований` | `requirements` | Run a quick feature-local sweep for stale old variants after a requirement edit. |
| `проверь консистентность требований` | `requirements` | Run a consistency sweep across affected artifacts. |
| `актуализируй прототипы` | `delivery-prototype` | Update prototypes listed in impact/backlog. |
| `общий прототип согласован` | `delivery-prototype` | Mark the root prototype as approved and only then use it as the source for slice handoff prototypes. |
| `обнови реальный прогресс` | `execution-update` | Update tasks, actual-progress gantt and Confluence export. |
| `собери puml без инклюдов` | `execution-update` | Create a standalone PlantUML export from an include-based gantt view. |
| `возьми срез в разработку` | `execution-update` | Prepare slice development context and handoff without changing planning baselines. |
| `разбери срез по коду` | `execution-update` | Use bounded research to map a ready slice onto code areas and risks. |
| `предложи план реализации` | `execution-update` | Draft an implementation plan tied to slice requirements and checks. |
| `проверь реализацию среза` | `execution-update` | Compare implementation state against slice requirements, prototype and checks. |
| `подготовь проверки по срезу` | `execution-update` | Draft QA checks and coverage for a ready slice. |
| `собери негативные сценарии` | `execution-update` | Draft negative and edge scenarios tied to slice requirements. |
| `сверь проверки с требованиями` | `execution-update` | Build or update a requirement-to-check coverage matrix. |
| `зафиксируй доменное решение` | `requirements` | Register decision and impact in `domain-impact.md`. |
| `собери релизный пакет` | `release-finalization` | Prepare release-level final artifacts. |
| `промоуть в baseline` | `release-finalization` | Promote release outputs into canonical baseline. |
| `откати решение DEC-*` | `release-finalization` | Start rollback flow for a known decision. |
| `проверь workflow` | any | Run validations and workflow checks. |

## Accepted synonyms

Treat these as equivalent user phrasings.

| Canonical command | Accepted synonyms |
|---|---|
| `новая фича` | `разбери новую фичу`, `сделай feature intake`, `сделай preflight по фиче`, `появилась новая фича`, `это новая фича` |
| `занимаемся планированием` | `переходим в планирование`, `давай планировать`, `давай займемся планированием`, `включаем planning`, `пора планировать` |
| `делаем требования` | `переходим к требованиям`, `давай требования`, `давай сделаем требования`, `пишем требования`, `соберем требования`, `включаем requirements`, `делаем требования в новом формате`, `делаем требования в старом формате` |
| `делаем презентационный прототип` | `делаем scope prototype`, `собери демо-прототип`, `делаем демо для заказчика`, `делаем макет для согласования`, `собери кликабельный макет для заказчика`, `нужен демо-макет`, `давай общий прототип` |
| `делаем прототип для разработки` | `делаем handoff prototype`, `делаем delivery prototype`, `собери прототип для фронта`, `делаем макет для фронта`, `собери handoff-макет`, `нужен макет для фронтендера` |
| `обновляем прогресс` | `переходим к прогрессу`, `фиксируем прогресс`, `давай обновим прогресс`, `обновим статус задач`, `зафиксируем факт`, `включаем execution update` |
| `финализируем релиз` | `переходим к релизу`, `собираем релиз`, `давай финализировать релиз`, `закрываем релизный цикл`, `готовим релизный пакет`, `включаем release finalization` |
| `актуализируй требования` | `обнови требования`, `синхронизируй требования`, `подтяни требования`, `приведи требования в актуальное состояние` |
| `проверь хвосты требований` | `дочисти хвосты`, `убери хвосты в требованиях`, `проверь старые упоминания`, `проверь что старый вариант нигде не остался`, `сделай локальную дочистку требований` |
| `проверь консистентность требований` | `сделай consistency sweep`, `проверь консистентность`, `сверь требования`, `проверь что ничего не разъехалось`, `сделай сверку требований` |
| `актуализируй прототипы` | `обнови прототипы`, `синхронизируй прототипы`, `подтяни прототипы`, `приведи макеты в актуальное состояние` |
| `обнови реальный прогресс` | `обнови actual progress`, `обнови actual-progress`, `зафиксируй прогресс`, `синхронизируй прогресс`, `обнови фактический прогресс`, `обнови план-факт` |
| `собери puml без инклюдов` | `собери puml для Confluence`, `собери PlantUML без include`, `разверни include в puml`, `дай standalone puml`, `собери гант для конфлюенса` |
| `возьми срез в разработку` | `подготовь срез к разработке`, `подготовь срез для разработки`, `начинаем разработку среза` |
| `разбери срез по коду` | `найди где реализовывать срез`, `сопоставь срез с кодом`, `разбери код под срез` |
| `предложи план реализации` | `собери план реализации среза`, `распиши реализацию среза`, `разложи реализацию по шагам` |
| `проверь реализацию среза` | `сверь реализацию со срезом`, `проверь код по срезу`, `проверь что срез реализован` |
| `подготовь проверки по срезу` | `собери тесты по срезу`, `подготовь тест-дизайн по срезу`, `собери QA-проверки` |
| `собери негативные сценарии` | `собери негативные кейсы`, `собери граничные сценарии`, `усиль тест-дизайн негативными сценариями` |
| `сверь проверки с требованиями` | `построй покрытие требований проверками`, `проверь покрытие тестами`, `сверь тест-дизайн с требованиями` |
| `зафиксируй доменное решение` | `зарегистрируй решение`, `зафиксируй decision`, `добавь domain decision`, `запиши доменное решение`, `оформи доменное решение`, `зарегистрируй DEC` |
| `собери релизный пакет` | `подготовь release package`, `собери release`, `зафиксируй релиз`, `подготовь пакет релиза`, `собери пакет релиза`, `подготовь релизный комплект` |
| `промоуть в baseline` | `обнови baseline`, `сделай baseline promotion`, `перенеси в baseline`, `зафиксируй новый baseline`, `обнови текущее состояние системы` |
| `откати решение DEC-*` | `rollback DEC-*`, `отмени решение DEC-*`, `сделай rollback по DEC-*`, `откати DEC-*`, `верни решение DEC-*` |
| `проверь workflow` | `проверь всё`, `прогони проверки`, `workflow check`, `проверь harness`, `сделай полный check`, `проверь структуру и ссылки` |

## Modes

- `planning`
- `requirements`
- `scope-prototype`
- `delivery-prototype`
- `execution-update`
- `release-finalization`

## Context Switch Commands

| User command | Target mode | Required first action |
|---|---|---|
| `новая фича` | `planning` | Switch mode, inspect source folder, run intake, do not scaffold yet. |
| `занимаемся планированием` | `planning` | Switch mode, read baseline/current and current quarter planning. |
| `делаем требования` | `requirements` | Switch mode, select new readable or old detailed format, read baseline/current and author the root feature requirements before deriving slices. |
| `делаем презентационный прототип` | `scope-prototype` | Switch mode, inspect existing prototypes/references and choose the common feature prototype base before writing. |
| `делаем прототип для разработки` | `delivery-prototype` | Switch mode, verify the root prototype exists and is explicitly approved in `prototype-notes.md`, otherwise stop without editing slice prototypes. |
| `обновляем прогресс` | `execution-update` | Switch mode, read planning actualization, execution tasks and team roster. |
| `возьми срез в разработку` | `execution-update` | Switch mode, read slice requirements/prototypes, gather context and prepare handoff. |
| `подготовь проверки по срезу` | `execution-update` | Switch mode, read slice requirements/prototypes and draft QA coverage. |
| `финализируем релиз` | `release-finalization` | Switch mode, read releases, domain-impact files, consistency backlog. |

## Workflow Commands

### Planning

| User command | Meaning | Main artifacts |
|---|---|---|
| `новая фича` | Run feature intake/preflight and separate baseline coverage from the new delta before scaffolding. | `planning/intake/*.md`, `baseline/current/*`, `features/*`, source folders |
| `спланируй квартал` | Build or update quarter planning structure and gantt. | `planning/<quarter>/gantt/*`, `features/*/planning/*` |
| `разложи фичу на planning stories` | Create/update planning stories with Summary, Description and role-split estimates. | `features/<feature>/planning/stories/*.md`, `estimates.md` |
| `подготовь HLE` | Prepare story-level decomposition and person-day estimates split by `AN / FE / BE / QA` for team discussion. | planning stories, `estimates.md`, scope prototype notes |
| `спланируй фичу` | Prepare feature planning context, planning stories, assumptions, risks and story/slice mapping. | `planning-context.md`, `assumptions.md`, `risk-register.md`, `story-map.md`, planning stories |
| `собери командирский план` | Produce buffered management plan from quarter plan. | `commander-plan.puml`, includes |
| `сравни план и факт` | Compare quarter/commander baseline with actual-progress. | gantt files, execution tasks |

### Requirements

| User command | Meaning | Main artifacts |
|---|---|---|
| `давай сделаем требования` | Create or update the root feature requirement page first, then derive slice detail packs from it. | `features/*/requirements.md`, `features/*/slices/*/requirements/*.md` |
| `делаем требования в новом формате` | Use the new readable templates: business context in root, short visual slice packs, tester checklists in every slice, PlantUML only. | `.workflow/templates/requirements/*.readable.template.md`, requirements |
| `делаем требования в старом формате` | Use the old detailed templates and preserve the earlier Confluence-style structure. | `.workflow/templates/requirements/feature-requirements.template.md`, requirements |
| `актуализируй требования` | Update living requirements and propagate consistency impact. | requirements, `domain-impact.md`, consistency backlog |
| `проверь хвосты требований` | Run a quick feature-local cleanup for stale old wording, endpoints, fields, statuses or option names after a requirements edit. | current feature requirements, slice packs, `domain-impact.md`, local backlog items |
| `проверь консистентность требований` | Run a consistency sweep across affected features and baseline. | requirements, `baseline/current/*`, `.workflow/consistency-backlog.md` |
| `разложи по срезам` | Derive semantic slice cards and detail packs from the root feature requirements, not just FE/BE. | `features/<feature>/slices/*` |
| `зафиксируй доменное решение` | Add Decision ID and impact record for a domain/business rule decision. | `domain-impact.md`, consistency backlog |

### Scope Prototype

| User command | Meaning | Main artifacts |
|---|---|---|
| `сделай презентационный прототип` | First choose a visual base, then build/update the common root feature prototype with fake data as a user-facing whole-feature mockup. | `features/<feature>/prototype.html`, `features/<feature>/prototype-notes.md` |
| `покажи ideal и MVP` | Make the common feature prototype demonstrate ideal target and MVP cut. | root feature prototype, prototype notes |
| `подготовь демо для заказчика` | Polish the common feature prototype for scope alignment presentation. | root feature prototype |

### Delivery Prototype

| User command | Meaning | Main artifacts |
|---|---|---|
| `сделай прототип для фронта` | Only after root prototype confirmation, build/update slice-level MUI handoff prototypes derived from it; otherwise stop without editing them. | `features/<feature>/slices/<slice>/delivery-prototype/*` |
| `актуализируй прототипы` | Update affected prototypes listed in domain-impact/backlog, starting from the common feature prototype when relevant. | affected prototype files |
| `актуализируй прототип по требованиям` | Align one delivery prototype with current slice requirements. | delivery prototype and notes |
| `общий прототип согласован` | Mark the root prototype as approved and only then use it as the source for slice-level handoff prototypes. | `features/<feature>/prototype.html`, `features/<feature>/prototype-notes.md`, `features/<feature>/slices/*/delivery-prototype/*` |

### Execution Update

| User command | Meaning | Main artifacts |
|---|---|---|
| `обнови реальный прогресс` | Update implementation tasks and regenerate actual-progress gantt plus standalone Confluence export. | `execution/tasks.md`, actualization, `.workflow/team.md`, gantt |
| `задача X завершена` | Mark implementation task done and adjust actual dates/progress. | task registry, actual-progress |
| `задачу X взял Y` | Set executor and actual/planned start for a task. | task registry, actual-progress |
| `добавь реальные задачи вместо story X` | Materialize planning story with implementation tasks. | task registry, `actualization.md` |
| `добавь milestone релиза` | Add release milestone to actual-progress/related gantt. | gantt preamble/include |
| `собери puml без инклюдов` | Expand an include-based PlantUML view into a standalone export file for Confluence or external sharing. | generated gantt view, standalone export puml |
| `возьми срез в разработку` | Prepare small-window slice context and implementation handoff for a ready slice. | `context-summary.md`, `implementation-handoff.md` |
| `разбери срез по коду` | Run bounded code research for a ready slice. | `.research/*.yaml`, `.research/summary.md`, handoff updates |
| `предложи план реализации` | Draft implementation tasks tied to requirements and verification. | `execution/implementation-plan.md` |
| `проверь реализацию среза` | Compare implementation state against requirements, prototype and verification. | implementation review notes, verification results |
| `подготовь проверки по срезу` | Draft QA checks and coverage for a ready slice. | `testing/test-plan.md` |
| `собери негативные сценарии` | Add negative and edge scenarios tied to requirements. | `testing/test-plan.md` |
| `сверь проверки с требованиями` | Ensure every accepted check traces to requirements and assumptions are marked. | coverage matrix |

### Release Finalization

| User command | Meaning | Main artifacts |
|---|---|---|
| `собери релизный пакет` | Create/update release package from delivered feature artifacts. | `releases/<quarter>/<release-id>/*` |
| `зафиксируй итоговые требования` | Copy/normalize final delivered requirements into release package. | release final requirements |
| `промоуть в baseline` | Promote release outputs into `baseline/current`. | baseline/current, baseline/versions, release notes |
| `откати решение DEC-*` | Handle rollback according to pre/post-release status. | domain-impact, backlog, release/baseline as needed |
| `закрой consistency backlog` | Propagate or explicitly defer open consistency items for release. | `.workflow/consistency-backlog.md`, impacted artifacts |

## Validation Commands

| User command | Meaning |
|---|---|
| `проверь структуру` | Run structure validation if available. |
| `проверь ссылки` | Run markdown link validation if available. |
| `пересобери гант` | Run gantt sync script for the active quarter. |
| `проверь workflow` | Run structure, links and relevant generated-artifact checks. |
| `проверь контекст` | Run context/research/handoff/test-plan validation if available. |
