# analyst-harness

`analyst-harness` - обвязка для долгоживущего продуктового знания: сначала формируется доменная DDD-модель, затем на ней строятся квартальное планирование, требования, прототипы, выполнение работ и финализация релизов.

Репозиторий рассчитан на терминальные LLM-инструменты и обычную ручную работу в проекте. Служебные правила и контракт агента живут в `AGENTS.md` и `.workflow/*`, а сам `README.md` нужен как понятная точка входа для человека.

## Как и что здесь устроено

- правила процесса хранятся в репозитории;
- сердцем проекта является доменная модель в логике DDD;
- канонический `baseline/current/` отделен от текущих и запланированных изменений;
- работа делится на режимы: планирование, требования, прототипирование, исполнение и финализация релиза;
- артефакты группируются по `feature`, затем по `slice`;
- прототипы делаются как одиночный `prototype.html` без сборки;
- все ключевые действия описываются короткими командами на русском.

## Кто чем занимается

### Аналитик

- разбирает входящие материалы;
- отделяет текущее поведение от новой дельты;
- выделяет `feature` и `slice`;
- ведет планирование, требования и презентационные прототипы.

### Разработчик

- берет `slice` в работу;
- разбирает реализацию по коду;
- готовит план реализации;
- доводит задачу до ревью.

### Тестировщик

- готовит проверки по `slice`;
- собирает негативные и граничные сценарии;
- сверяет проверки с требованиями;
- фиксирует пробелы и возвраты в требования.

### Служебные режимы

- `planning` - квартальное и командирское планирование;
- `requirements` - требования по фиче и срезам;
- `scope-prototype` - быстрый демо-прототип для уточнения формы решения;
- `delivery-prototype` - точный прототип для передачи в разработку;
- `execution-update` - актуализация факта выполнения;
- `release-finalization` - финализация релиза и промоушен в baseline.

Утверждённые квартальный и командирский планы являются неизменяемым baseline. Позднее обнаруженный scope отображается через task candidates и actual-progress.

## Команды по ролям

Работать здесь удобнее через LLM: человек называет команду, а LLM сама переключает режим и при необходимости запускает нужные скрипты.

### Аналитик

- `новая фича` - разобрать входные материалы и выделить дельту;
- `занимаемся планированием` - собрать оценки, риски и квартальный план;
- `делаем требования` - оформить требования по фиче;
- `делаем презентационный прототип` - собрать общий прототип для согласования;
- `создай прототип среза для фронта` - подготовить handoff-прототип конкретного среза.

### Разработчик

- `возьми срез в разработку` - начать работу над срезом;
- `разбери срез по коду` - посмотреть затронутую реализацию;
- `предложи план реализации` - составить план работ;
- `начни реализацию` - приступить к коду;
- `проверь реализацию среза` - проверить готовый результат;
- `подготовь к ревью` - собрать результат к проверке.

### Тестировщик

- `подготовь проверки по срезу` - собрать тест-дизайн;
- `собери негативные сценарии` - выделить отрицательные и граничные случаи;
- `сверь проверки с требованиями` - проверить покрытие;
- `проверь прототип по срезу` - оценить прототип;
- `проверь реализацию по срезу` - оценить готовую реализацию;
- `зафиксируй найденные пробелы` - вернуть расхождения в требования или план.

## Что лежит в репозитории

- `core/` - постоянные правила и концептуальная модель;
- `modes/` - правила каждого режима;
- `prompts/` - готовые текстовые заготовки под роли и режимы;
- `templates/` - шаблоны для планирования, требований, прототипов и исполнения;
- `scripts/` - скрипты scaffold и проверки;
- `adapters/cli/` - shell-помощники для переключения режима и старта сессии;
- `adapters/vscodium/` - настройки, задачи и сниппеты для VSCodium;
- `examples/demo-project/` - пример раскладки готового проекта;
- `AGENTS.md` - служебный контракт работы агента в этом репозитории.

## Быстрый старт

### 1. Создайте новый проект

Рекомендуемый путь - использовать scaffold-скрипт:

```bash
bash scripts/scaffold-project.sh /path/to/project
```

Он создает структуру проекта и кладет в нее:

- `.workflow/llm-contract.md`;
- `.workflow/agent-delegation.md`;
- `.workflow/skills-policy.md`;
- `.workflow/tooling-policy.md`;
- `.workflow/context-policy.md`;
- `.workflow/research-policy.md`;
- `.workflow/active-mode.md`;
- `.workflow/modes/*.md`;
- `.workflow/overrides/`;
- `.workflow/command-catalog.md`;
- `.workflow/command-cheatsheet.md`;
- `.workflow/consistency-backlog.md`;
- `.workflow/team.md`;
- `.workflow/tools/`;
- `.workflow/run-state/`;
- `.workflow/templates/`;
- `baseline/current/`;
- `baseline/versions/`;
- `context/`;
- `features/`;
- `planning/intake/`;
- `releases/`;
- `AGENTS.md`.

Если нужен ручной путь без запуска `sh`-скрипта, можно сделать копию репозитория через `git clone`, затем удалить `.git`, переименовать папку и работать уже в этой копии как в новом проекте.

Пример:

```bash
git clone <repo-url> my-project
cd my-project
rm -rf .git
```

Этот способ подходит как ручная заготовка, но после него нужно самому проверить, что в копии есть все нужные каталоги и файлы из списка выше.

### 2. Заполните команду

В новом проекте заполните `.workflow/team.md`:

- кто входит в команду;
- какая у каждого роль;
- какой lane ему назначен;
- какая у него capacity.

Если для проекта нужны собственные формулировки команд, поправьте:

- `.workflow/command-catalog.md`;
- `.workflow/command-cheatsheet.md`.

### 3. Сформируйте доменную модель

До разгона планов и срезов стоит зафиксировать предметную область:

- какие сущности существуют;
- какие у них границы и связи;
- какие бизнес-правила неизменны;
- какие состояния и переходы считаются каноническими;
- что уже находится в `baseline/current/`, а что является новой дельтой.

В этой обвязке это центральная точка старта: сначала доменная модель, потом планирование и требования.

Каноническое текущее состояние доменной модели хранится в `baseline/current/domain/`:

- `baseline/current/domain/ubiquitous-language.md`;
- `baseline/current/domain/bounded-contexts.md`;
- `baseline/current/domain/aggregates.md`;
- `baseline/current/domain/business-rules.md`;
- `baseline/current/domain/state-machines/README.md`.

Когда появляется новая дельта, ее сначала описывают в фиче, а затем переносят в baseline после релиза. Для формирования доменной модели удобно опираться на уже существующие требования и команду LLM, например:

- `делаем требования` - если нужно собрать или обновить требования по фиче на основе текущих материалов;
- `новая фича` - если сначала надо выделить дельту и только потом расписать доменную модель;
- `занимаемся планированием` - если нужно связать доменную модель с квартальным планом и рисками;
- `делаем требования` + `разложи требования на срезы` - если доменную модель уже надо разнести на проверяемые срезы.

Если пользователь уже знает путь к требованиям системы, можно просить LLM сформировать доменную модель прямо по ним:

- `Сформируй доменную модель по требованиям из /path/to/requirements`;
- `Возьми требования из /path/to/project/features/deployments/requirements и собери по ним доменную модель`;
- `Посмотри требования в /path/to/project/baseline/current/requirements и опиши по ним доменную модель текущей системы`;
- `По требованиям из /path/to/project/features/deployments/slices/form-editing/requirements собери доменную модель и перечисли, что должно попасть в baseline/current/domain/`.

### 4. Попросите LLM переключить режим

Например:

- `переведи проект в режим планирования`;
- `переведи проект в режим требований`;
- `подготовь старт сессии для проекта`.

Если нужно, LLM сама вызовет `switch-mode.sh` или `start-session.sh`.

### 5. Начните работу

Дальше можно просить LLM поднимать квартал, фичи и срезы:

- `создай квартал 2026-Q2`;
- `создай фичу deployments`;
- `создай срез form-editing для фичи deployments`.

При необходимости LLM сама вызовет соответствующие scaffold-скрипты из репозитория `analyst-harness`.

## Исполняемый harness

Внутренний CLI не заменяет ролевые команды, а делает правила проверяемыми:

```bash
python .workflow/tools/harnessctl.py doctor .
python .workflow/tools/harnessctl.py session-brief . --feature <feature> --slice <slice>
python .workflow/tools/harnessctl.py run-init . planning --feature <feature>
```

Черновые квартальный и командирский планы генерируются из ролевых stories:

```bash
python .workflow/tools/sync-planning-gantt.py . 2026-Q3
```

После перевода `planning/<quarter>/plan-state.md` в `approved` эти планы больше не регенерируются. Новая фактическая работа появляется в actual-progress.

### Версия и управляемые файлы

Текущая версия harness хранится в `VERSION`. При scaffold в проект создаётся `.workflow/harness.json`, где фиксируются:

- schema version;
- версия и commit harness;
- признак dirty source checkout;
- hashes установленных managed-файлов;
- список project-owned путей.

Managed-файлы включают контракты, режимы, внутренние skills, шаблоны и инструменты. Они обновляются только через `harnessctl upgrade`. Project-owned файлы принадлежат конкретному проекту и не перезаписываются обновлением:

- `.workflow/active-mode.md`;
- `.workflow/team.md`;
- `.workflow/code-repos.json`;
- `.workflow/evals/`;
- `.workflow/overrides/`;
- `.workflow/run-state/`;
- `.workflow/runs/`;
- `README.md` проекта.

Проверить различия перед обновлением:

```bash
python /path/to/analyst-harness/scripts/harnessctl.py diff /path/to/project \
  --source /path/to/analyst-harness
```

Выполнить conflict-safe обновление:

```bash
python /path/to/analyst-harness/scripts/harnessctl.py upgrade /path/to/project \
  --source /path/to/analyst-harness --apply
```

Если managed-файл был изменён локально, upgrade сообщает `CONFLICT` и ничего не перезаписывает. Проектное отличие нужно либо перенести в harness, либо оформить в `.workflow/overrides/`.

### Безопасный scaffold

Scaffold-команды не перезаписывают существующие знания по умолчанию:

```bash
bash scripts/scaffold-project.sh /path/to/project
bash scripts/scaffold-project.sh /path/to/project --merge
bash scripts/scaffold-feature.sh /path/to/project feature-slug --merge
bash scripts/scaffold-slice.sh /path/to/project feature-slug slice-slug --merge
```

- обычный запуск требует пустой target;
- `--merge` добавляет только отсутствующие harness-файлы;
- `--force` является явной операцией перезаписи scaffold-файлов;
- project merge не создаёт placeholder-файлы внутри существующих `baseline/`, `features/`, `planning/` и `context/`.

## Подробная модель планирования

### Фича и planning stories

Фича является законченной пользовательской или системной ценностью квартала. Planning story — не функциональный срез, а ролевой поток работ внутри фичи.

На одну фичу допускается максимум четыре planning stories:

- `STORY-<FEATURE>-AN`;
- `STORY-<FEATURE>-BE`;
- `STORY-<FEATURE>-FE`;
- `STORY-<FEATURE>-QA`.

Если работа конкретной роли не нужна, соответствующая story отсутствует. Функциональная декомпозиция выполняется позднее в requirements mode через slices.

### Оценка и длительность

Для каждой role story сохраняются:

- analyst anchor effort;
- team effort;
- явно согласованный effort;
- max parallelism;
- efficiency;
- зависимости;
- ограничение `not before`.

Итоговая оценка не вычисляется усреднением. Она считается принятой только после явного согласования.

Длительность рассчитывается так:

```text
ceil(agreed effort / effective parallel capacity)
```

Default efficiency:

- `AN = 0.80`;
- `BE = 0.70`;
- `FE = 0.65`;
- `QA = 0.80`.

Role efficiency может быть переопределена в story, а персональный коэффициент — в `.workflow/team.md`.

### Ресурсы и приоритет

- `gantt/order.txt` хранит приоритет фич сверху вниз;
- готовая работа более приоритетной фичи первой получает подходящие ресурсы;
- свободная роль может перейти к следующей фиче, пока в верхней фиче для неё нет готовой работы;
- нижняя фича не должна задерживать ставшую доступной работу верхней;
- автоматическое прерывание уже начатой работы не выполняется;
- загрузка ресурса не превышает 100%;
- отпуска и другие закрытые интервалы задаются в `.workflow/team.md`;
- плановая role story может использовать несколько ресурсов до `max_parallelism`;
- фактическая задача всегда назначается одному человеку.

Стандартные зависимости: `AN -> BE`, `AN -> FE`, `BE + FE -> QA`. FE стартует не раньше трёх открытых рабочих дней после старта BE. Если BE отсутствует, FE стартует после AN либо в первое доступное окно.

### Quarter и commander plan

`quarter-plan` строится по согласованным effort без commander buffer. `commander-plan` использует те же scope, порядок и зависимости, но добавляет risk buffer:

- минимум 20%;
- 30% для высокого риска или внешней зависимости;
- 40% для нескольких высоких рисков, новой интеграции или неясной модели данных;
- 50% для критической неопределённости или неподтверждённой архитектуры;
- более 50% требует ручного решения.

Buffer влияет на длительности и даты commander plan, но не показывается руководству отдельной полосой.

### Утверждение и неизменяемость

План имеет состояния `draft` и `approved`. Только владелец проекта утверждает план:

```bash
python .workflow/tools/harnessctl.py plan-approve . 2026-Q3 --by <owner>
```

При утверждении сохраняются hashes master PlantUML, feature includes и baseline-колонок actualization maps. После этого:

- quarter-plan и commander-plan не регенерируются;
- baseline start/duration в actualization не меняются;
- новый scope появляется как task candidates или actual tasks;
- actual-progress остаётся единственным изменяемым представлением реального положения дел;
- `validate-planning.py` обнаруживает любую правку утверждённого baseline.

### Ретроспектива

После квартала:

```bash
python .workflow/tools/calibrate-planning.py . 2026-Q3
```

Инструмент сравнивает role effort с длительностью фактических задач и предлагает новые efficiency/risk значения. Предложения применяются только к будущим draft-планам и никогда не переписывают историю.

## Требования, влияния и task candidates

Root requirements являются authored source. Slice cards, FE/BE packs, task candidates, implementation plans и QA coverage являются производными.

После изменения требований выполняются два прохода:

1. Обновление root requirements и всех непосредственно производных срезов.
2. Поиск устаревших endpoint, полей, статусов, ролей, терминов, прототипов и соседних правил.

Локальный необъяснённый хвост блокирует завершение. Cross-mode работа может быть отложена только конкретной записью в consistency backlog.

Обязательные изменения соседних фич включаются в scope инициирующей фичи и раздел `Доработки затронутых фич`. Каждая строка должна быть покрыта `REQ-*`, task candidate и проверкой либо иметь явное `not applicable` с причиной.

Task candidates создаются вместе с детальными требованиями среза:

- одна роль;
- один смыслово законченный результат;
- отдельный commit/PR boundary;
- ссылки на `REQ-*`/`AC-*`;
- зависимость и обязательная verification;
- целевой размер BE/FE/QA 1–3 дня;
- максимум BE 5 дней, FE/QA 10 дней;
- для AN размер не ограничивается.

## Исполнительские циклы

Состояние каждого цикла хранится в `.workflow/runs/<run-id>/run.json`. Общий loop:

```text
orient -> plan -> bounded action -> deterministic verify
       -> independent review -> checkpoint -> continue/complete/escalate
```

Создание циклов:

```bash
python .workflow/tools/harnessctl.py run-init . planning --feature <feature>
python .workflow/tools/harnessctl.py run-init . requirements --feature <feature>
python .workflow/tools/harnessctl.py run-init . implementation --feature <feature> --slice <slice> --role BE
python .workflow/tools/harnessctl.py run-init . qa --feature <feature> --slice <slice> --role QA
```

`implementation` и `qa` используют `.workflow/code-repos.json`. Run сохраняет hashes входных требований. Если они меняются во время работы, `run-verify` возвращает ошибку freshness и требует обновить work packet.

Verifier задаётся массивом аргументов без shell-интерпретации:

```json
{
  "name": "targeted tests",
  "argv": ["pytest", "tests/test_slice.py"],
  "cwd": "."
}
```

Запуск:

```bash
python .workflow/tools/harnessctl.py run-verify .workflow/runs/<run-id>/run.json
```

Повторяющийся failure после заданного лимита переводит run в `escalated`.

## Диагностика и evals

`harnessctl doctor` объединяет structural, workflow, link, context, planning и trace checks. `--strict` переводит предупреждения context/trace в ошибки.

Синтетические evals проверяют clean scaffold, mode mismatch, destructive scaffold и approved-plan tampering:

```bash
python scripts/evaluate-harness.py
```

Проектные golden-сценарии живут в `.workflow/evals/golden-scenarios.json`:

```bash
python .workflow/tools/evaluate-harness.py .
```

Они предназначены для низкодрейфовых доменных инвариантов, а не для копирования полного набора требований в eval-конфигурацию.

## Типовой рабочий цикл

1. `новая фича` - разобрать исходные материалы и выделить дельту.
2. `занимаемся планированием` - подготовить оценки, риски и квартальный план.
3. `делаем требования` - оформить требования по фиче.
4. `делаем презентационный прототип` - собрать прототип для согласования.
5. `делаем прототип для разработки` - подготовить handoff-прототип для среза.
6. `возьми срез в разработку` - начать реализацию среза.
7. `подготовь проверки по срезу` - подготовить тест-дизайн и покрытие.
8. `финализируем релиз` - зафиксировать результат и промоутить в baseline.

## Проверки

После изменений проекта проверьте структуру и ссылки:

```bash
python .workflow/tools/validate-structure.py .
python .workflow/tools/validate-links.py .
python .workflow/tools/validate-context.py .
python .workflow/tools/harnessctl.py doctor .
python .workflow/tools/find-stale-terms.py . <старый-термин> [<ещё-термин> ...]
```

После правок gantt:

```bash
python .workflow/tools/sync-quarter-gantt.py planning/2026-Q2/gantt
python .workflow/tools/sync-actual-progress-overlay.py planning/2026-Q2/gantt
```

Если нужно развернуть PlantUML include-файлы для рендерера, который их не понимает:

```bash
python .workflow/tools/expand-plantuml-includes.py
```

## Стандарт прототипов

Все прототипы делаются как одиночный файл `prototype.html`:

- React 18 через CDN;
- ReactDOM через CDN;
- MUI через CDN;
- Babel standalone.

Такой прототип можно открыть локально, показать через Live Preview или отправить как один файл.

## Как читать структуру проекта

- `baseline/current/` - текущее каноническое состояние системы;
- `baseline/versions/` - предыдущие версии baseline;
- `features/` - папки по отдельным фичам;
- `planning/` - квартальные планы и intake-заметки;
- `planning/intake/` - preflight-заметки перед scaffold новой фичи;
- `context/` - исходные материалы и описания текущей системы;
- `releases/` - неизменяемые release-пакеты перед промоушеном в baseline.

## Коротко о том, как не запутаться

- сначала создается или копируется проект;
- потом фиксируется команда и активный режим;
- затем фича идет через planning, requirements, прототипы, execution и release;
- `baseline/current/` обновляется только после финализации релиза;
- в спорных случаях источником истины остается markdown в репозитории.
