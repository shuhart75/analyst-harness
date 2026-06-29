# analyst-harness

`analyst-harness` - обвязка для долгоживущего продуктового знания: базовая модель предметной области, квартальное планирование, требования, прототипы, выполнение работ и финализация релизов.

Репозиторий рассчитан на терминальные LLM-инструменты и обычную ручную работу в проекте. Служебные правила и контракт агента живут в `AGENTS.md` и `.workflow/*`, а сам `README.md` нужен как понятная точка входа для человека.

## Что здесь устроено

- правила процесса хранятся в репозитории, а не в одной IDE;
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

Если у проекта нужны собственные формулировки команд, поправьте:

- `.workflow/command-catalog.md`;
- `.workflow/command-cheatsheet.md`.

### 3. Переключите режим

```bash
bash adapters/cli/switch-mode.sh /path/to/project planning
```

### 4. Начните работу

Для терминального LLM-воркфлоу есть помощник старта сессии:

```bash
bash adapters/cli/start-session.sh /path/to/project
```

Он показывает стартовые служебные файлы и текущий режим проекта.

### 5. Добавляйте квартал, фичи и срезы

Скрипты scaffold для квартала, фичи и среза запускаются из репозитория `analyst-harness`, передавая путь к проекту:

```bash
bash scripts/scaffold-quarter.sh /path/to/project 2026-Q2
bash scripts/scaffold-feature.sh /path/to/project deployments
bash scripts/scaffold-slice.sh /path/to/project deployments form-editing
```

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
python .workflow/tools/find-stale-terms.py .
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
