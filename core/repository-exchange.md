# Защищённые Git-операции collaboration

Этот внутренний договор обслуживает только многопользовательские feature-ветки единственного рабочего репозитория `PROJECT_ROOT`. Приём reverse patch регулируется отдельно файлом `core/reverse-patch.md`.

## Операции

- `repository-exchange.py update-feature-branch` получает `origin/main` и выполняет fast-forward либо обычный merge в текущую `feature/<feature>/<analyst>`.
- `repository-exchange.py fast-forward-analytics-main` обновляет только чистую локальную `main`, если она является предком `origin/main`.
- `repository-exchange.py inspect-analytics-origin-conflict` диагностирует конфликт без потери сторон.
- `list-analytics-snapshots`, `inspect-analytics-snapshot` и `restore-analytics-snapshot-file` дают точечное восстановление из защитных снимков.

## Защитные снимки

Перед fast-forward или merge создаются локальные Git refs и метаданные под `.workspace-state/analytics-snapshots/`. При конфликте сохраняются base, local и incoming версии каждого конфликтующего пути. Снимки не отправляются в remote и не удаляются автоматически.

Восстановление разрешено только для одного явно выбранного пути и одной стороны. Оно не индексирует и не коммитит файл автоматически.

## Запреты

- прямой push feature-работы в `main`;
- rebase, reset, force push;
- `git add -A`, `git add .` и широкое восстановление каталогов;
- автоматический выбор стороны конфликта;
- запуск этих операций для приёма reverse patch.

Reverse patch применяется только через `reverse_patch.py` на чистой `main` после закрытия collaboration-сессии.
