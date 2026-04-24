# Command Catalog

This file documents short natural-language commands that switch context or trigger recurring workflow actions.

## Interpretation rules

- Commands are intent shortcuts, not magic shell commands.
- If a command implies a mode switch, update `.workflow/active-mode.md` or explicitly state that the user should switch mode if the runtime cannot edit it.
- After a mode switch, read the target mode file before editing artifacts.
- If a command includes a folder/path, inspect that path before writing outputs.
- If a command causes cross-feature/domain impact, update `features/*/domain-impact.md` and `.workflow/consistency-backlog.md` as needed.
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
Нужно разложить доработку на planning stories, дать HLE в человеко-днях и обновить quarter-plan/commander-plan.
```

```text
делаем требования
В папке `context/source-materials/change-requests/packages-filtering` лежат текущие требования и новые скрины.
Нужно подготовить requirement pack по feature/slice, обновить domain-impact и перечислить затронутые прототипы.
```

```text
обновляем прогресс
RSCON-2445 завершена вчера, RSCON-2451 взял второй фронтендер позавчера.
Добавь milestone релиза на 2026-04-30 и обнови actual-progress.
```

| Core command | Mode | Primary intent |
|---|---|---|
| `новая фича` | `planning` | Run feature intake/preflight before any scaffold step. |
| `занимаемся планированием` | `planning` | Switch into quarter planning and HLE mode. |
| `делаем требования` | `requirements` | Switch into living requirements mode. |
| `делаем презентационный прототип` | `scope-prototype` | Switch into planning-stage prototype mode. |
| `делаем прототип для разработки` | `delivery-prototype` | Switch into handoff prototype mode. |
| `обновляем прогресс` | `execution-update` | Switch into implementation tracking mode. |
| `финализируем релиз` | `release-finalization` | Switch into release/baseline promotion mode. |
| `актуализируй требования` | `requirements` | Update requirements and propagate impact. |
| `проверь консистентность требований` | `requirements` | Run a consistency sweep across affected artifacts. |
| `актуализируй прототипы` | `delivery-prototype` | Update prototypes listed in impact/backlog. |
| `обнови реальный прогресс` | `execution-update` | Update tasks and actual-progress gantt. |
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
| `делаем требования` | `переходим к требованиям`, `давай требования`, `давай сделаем требования`, `пишем требования`, `соберем требования`, `включаем requirements` |
| `делаем презентационный прототип` | `делаем scope prototype`, `собери демо-прототип`, `делаем демо для заказчика`, `делаем макет для согласования`, `собери кликабельный макет для заказчика`, `нужен демо-макет` |
| `делаем прототип для разработки` | `делаем handoff prototype`, `делаем delivery prototype`, `собери прототип для фронта`, `делаем макет для фронта`, `собери handoff-макет`, `нужен макет для фронтендера` |
| `обновляем прогресс` | `переходим к прогрессу`, `фиксируем прогресс`, `давай обновим прогресс`, `обновим статус задач`, `зафиксируем факт`, `включаем execution update` |
| `финализируем релиз` | `переходим к релизу`, `собираем релиз`, `давай финализировать релиз`, `закрываем релизный цикл`, `готовим релизный пакет`, `включаем release finalization` |
| `актуализируй требования` | `обнови требования`, `синхронизируй требования`, `подтяни требования`, `приведи требования в актуальное состояние` |
| `проверь консистентность требований` | `сделай consistency sweep`, `проверь консистентность`, `сверь требования`, `проверь что ничего не разъехалось`, `сделай сверку требований` |
| `актуализируй прототипы` | `обнови прототипы`, `синхронизируй прототипы`, `подтяни прототипы`, `приведи макеты в актуальное состояние` |
| `обнови реальный прогресс` | `обнови actual progress`, `обнови actual-progress`, `зафиксируй прогресс`, `синхронизируй прогресс`, `обнови фактический прогресс`, `обнови план-факт` |
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
| `делаем требования` | `requirements` | Switch mode, read baseline/current, source materials, feature docs. |
| `делаем презентационный прототип` | `scope-prototype` | Switch mode, read feature scope and planning stories. |
| `делаем прототип для разработки` | `delivery-prototype` | Switch mode, read slice requirements and project UI constraints. |
| `обновляем прогресс` | `execution-update` | Switch mode, read planning actualization and execution tasks. |
| `финализируем релиз` | `release-finalization` | Switch mode, read releases, domain-impact files, consistency backlog. |

## Workflow Commands

### Planning

| User command | Meaning | Main artifacts |
|---|---|---|
| `новая фича` | Run feature intake/preflight and separate baseline coverage from the new delta before scaffolding. | `planning/intake/*.md`, `baseline/current/*`, `features/*`, source folders |
| `спланируй квартал` | Build or update quarter planning structure and gantt. | `planning/<quarter>/gantt/*`, `features/*/planning/*` |
| `разложи фичу на planning stories` | Create/update planning stories with Summary, Description and estimates. | `features/<feature>/planning/stories/*.md`, `estimates.md` |
| `подготовь HLE` | Prepare story-level decomposition and person-day estimates for team discussion. | planning stories, `estimates.md`, scope prototype notes |
| `собери командирский план` | Produce buffered management plan from quarter plan. | `commander-plan.puml`, includes |
| `сравни план и факт` | Compare quarter/commander baseline with actual-progress. | gantt files, execution tasks |

### Requirements

| User command | Meaning | Main artifacts |
|---|---|---|
| `давай сделаем требования` | Create feature/slice requirement packs from baseline and source materials. | `features/*/slices/*/requirements/*.md` |
| `актуализируй требования` | Update living requirements and propagate consistency impact. | requirements, `domain-impact.md`, consistency backlog |
| `проверь консистентность требований` | Run a consistency sweep across affected features and baseline. | requirements, `baseline/current/*`, `.workflow/consistency-backlog.md` |
| `разложи по срезам` | Split a feature into semantic slices, not just FE/BE. | `features/<feature>/slices/*` |
| `зафиксируй доменное решение` | Add Decision ID and impact record for a domain/business rule decision. | `domain-impact.md`, consistency backlog |

### Scope Prototype

| User command | Meaning | Main artifacts |
|---|---|---|
| `сделай презентационный прототип` | Build/update clickable planning-stage prototype with fake data. | `features/<feature>/planning/scope-prototype/*` |
| `покажи ideal и MVP` | Make prototype demonstrate ideal target and MVP cut. | scope prototype, planning notes |
| `подготовь демо для заказчика` | Polish scope prototype for scope alignment presentation. | scope prototype |

### Delivery Prototype

| User command | Meaning | Main artifacts |
|---|---|---|
| `сделай прототип для фронта` | Build/update slice-level MUI delivery prototype. | `features/<feature>/slices/<slice>/delivery-prototype/*` |
| `актуализируй прототипы` | Update affected prototypes listed in domain-impact/backlog. | affected prototype files |
| `актуализируй прототип по требованиям` | Align one delivery prototype with current slice requirements. | delivery prototype and notes |

### Execution Update

| User command | Meaning | Main artifacts |
|---|---|---|
| `обнови реальный прогресс` | Update implementation tasks and regenerate actual-progress gantt. | `execution/tasks.md`, actualization, gantt |
| `задача X завершена` | Mark implementation task done and adjust actual dates/progress. | task registry, actual-progress |
| `задачу X взял Y` | Set executor and actual/planned start for a task. | task registry, actual-progress |
| `добавь реальные задачи вместо story X` | Materialize planning story with implementation tasks. | task registry, `actualization.md` |
| `добавь milestone релиза` | Add release milestone to actual-progress/related gantt. | gantt preamble/include |

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
