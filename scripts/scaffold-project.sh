#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <target-project-dir>"
  exit 1
fi

TARGET="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$TARGET/.workflow/modes" "$TARGET/.workflow/overrides" "$TARGET/.workflow/tools" "$TARGET/.workflow/templates/requirements" "$TARGET/.workflow/templates/intake" "$TARGET/.workflow/templates/prototypes" "$TARGET/.vscode"
mkdir -p "$TARGET/context/source-materials/current-system/requirements" "$TARGET/context/source-materials/current-system/screenshots" "$TARGET/context/source-materials/current-system/prototypes" "$TARGET/context/source-materials/current-system/diagrams" "$TARGET/context/source-materials/change-requests"
mkdir -p "$TARGET/context/current-system" "$TARGET/context/change-requests"
mkdir -p "$TARGET/baseline/current/domain/state-machines" "$TARGET/baseline/current/requirements" "$TARGET/baseline/current/api" "$TARGET/baseline/current/ui" "$TARGET/baseline/current/data" "$TARGET/baseline/current/decisions" "$TARGET/baseline/versions"
mkdir -p "$TARGET/planning/intake" "$TARGET/features" "$TARGET/releases"

cp "$ROOT_DIR/AGENTS.md" "$TARGET/AGENTS.md"
cp "$ROOT_DIR/core/llm-contract.md" "$TARGET/.workflow/llm-contract.md"
cp "$ROOT_DIR/core/agent-delegation.md" "$TARGET/.workflow/agent-delegation.md"
cp "$ROOT_DIR/core/skills-policy.md" "$TARGET/.workflow/skills-policy.md"
cp "$ROOT_DIR/core/tooling-policy.md" "$TARGET/.workflow/tooling-policy.md"
cp "$ROOT_DIR/adapters/cli/switch-mode.sh" "$TARGET/.workflow/tools/switch-mode.sh"
cp "$ROOT_DIR/adapters/cli/start-session.sh" "$TARGET/.workflow/tools/start-session.sh"
cp "$ROOT_DIR/scripts/validate-structure.py" "$TARGET/.workflow/tools/validate-structure.py"
cp "$ROOT_DIR/scripts/validate-links.py" "$TARGET/.workflow/tools/validate-links.py"
cp "$ROOT_DIR/scripts/sync-quarter-gantt.py" "$TARGET/.workflow/tools/sync-quarter-gantt.py"
cp "$ROOT_DIR/scripts/sync-actual-progress-overlay.py" "$TARGET/.workflow/tools/sync-actual-progress-overlay.py"
cp "$ROOT_DIR/scripts/find-stale-terms.py" "$TARGET/.workflow/tools/find-stale-terms.py"
cp "$ROOT_DIR/scripts/expand-plantuml-includes.py" "$TARGET/.workflow/tools/expand-plantuml-includes.py"
chmod +x "$TARGET/.workflow/tools/switch-mode.sh"
chmod +x "$TARGET/.workflow/tools/start-session.sh"
chmod +x "$TARGET/.workflow/tools/find-stale-terms.py"
chmod +x "$TARGET/.workflow/tools/expand-plantuml-includes.py"
cp "$ROOT_DIR/adapters/vscodium/settings.json" "$TARGET/.vscode/settings.json"
cp "$ROOT_DIR/adapters/vscodium/tasks.json" "$TARGET/.vscode/tasks.json"
cp "$ROOT_DIR/adapters/vscodium/snippets.code-snippets" "$TARGET/.vscode/workflow.code-snippets"
cp "$ROOT_DIR/templates/requirements/README.md" "$TARGET/.workflow/templates/requirements/README.md"
cp "$ROOT_DIR/templates/requirements/feature-requirements.template.md" "$TARGET/.workflow/templates/requirements/feature-requirements.template.md"
cp "$ROOT_DIR/templates/requirements/slice.template.md" "$TARGET/.workflow/templates/requirements/slice.template.md"
cp "$ROOT_DIR/templates/requirements/frontend.template.md" "$TARGET/.workflow/templates/requirements/frontend.template.md"
cp "$ROOT_DIR/templates/requirements/backend.template.md" "$TARGET/.workflow/templates/requirements/backend.template.md"
cp "$ROOT_DIR/templates/intake/README.md" "$TARGET/.workflow/templates/intake/README.md"
cp "$ROOT_DIR/templates/intake/feature-intake.template.md" "$TARGET/.workflow/templates/intake/feature-intake.template.md"
cp "$ROOT_DIR/templates/prototypes/README.md" "$TARGET/.workflow/templates/prototypes/README.md"
cp "$ROOT_DIR/templates/prototypes/prototype.html.template" "$TARGET/.workflow/templates/prototypes/prototype.html.template"
cp "$ROOT_DIR/templates/prototypes/feature-prototype-notes.template.md" "$TARGET/.workflow/templates/prototypes/feature-prototype-notes.template.md"
cp "$ROOT_DIR/templates/prototypes/scope-prototype-notes.template.md" "$TARGET/.workflow/templates/prototypes/scope-prototype-notes.template.md"
cp "$ROOT_DIR/templates/prototypes/delivery-prototype-notes.template.md" "$TARGET/.workflow/templates/prototypes/delivery-prototype-notes.template.md"

for mode in planning requirements scope-prototype delivery-prototype execution-update release-finalization; do
  cp "$ROOT_DIR/modes/${mode}.md" "$TARGET/.workflow/modes/${mode}.md"
done

cat > "$TARGET/.workflow/active-mode.md" <<EOF2
# Active Mode

mode: planning

## Mode File
.workflow/modes/planning.md
EOF2

cat > "$TARGET/.workflow/overrides/terminology.md" <<'EOF2'
# Terminology Override

- Требования и рабочие артефакты по умолчанию пишем на русском.
- Английские термины допускаются в скобках для однозначности.
- Пути, slug и технические идентификаторы оформляем латиницей.
EOF2

cat > "$TARGET/.workflow/overrides/requirements-rules.md" <<'EOF2'
# Requirements Rules Override

- Канонический шаблон requirements лежит в `.workflow/templates/requirements/`.
- Backend-требования должны включать OpenAPI-фрагмент и примеры запросов/ответов.
- Описание модели данных оформляется markdown-таблицей.
- Requirement packs живые и могут дополняться в ходе разработки до релизной фиксации.
EOF2

cat > "$TARGET/.workflow/overrides/design-system-rules.md" <<'EOF2'
# Design System Rules Override

- Прототипы по умолчанию делаем на React + MUI без build step.
- Для handoff предпочтительны узнаваемые MUI-компоненты, чтобы фронтендер сразу видел будущую реализацию.
EOF2

cat > "$TARGET/.workflow/overrides/prototyping-rules.md" <<'EOF2'
# Prototyping Rules Override

- Scope prototype и delivery prototype по умолчанию оформляются как single-file \`prototype.html\`.
- Прототип должен открываться локально без сборки и быть пригоден для отправки одним файлом.
EOF2

cat > "$TARGET/.workflow/overrides/baseline-rules.md" <<'EOF2'
# Baseline Rules Override

- `baseline/current/` — это каноническое описание текущей deployed-системы.
- Сырые материалы складываются в `context/source-materials/` и не считаются source of truth, пока не промоутированы в baseline.
- Все итоговые delivered-требования перед промоушеном в baseline сначала фиксируются в `releases/`.
EOF2

cat > "$TARGET/.workflow/overrides/gantt-rules.md" <<'EOF2'
# Gantt Rules Override

- Заголовок gantt генерируется скриптом, руками правим только include/preamble файлы и \`closed-days.txt\`.
- Праздники и нерабочие дни квартала хранятся в \`planning/<quarter>/gantt/closed-days.txt\`.
- Общие служебные блоки перед feature lanes кладём в \`planning/<quarter>/gantt/preamble/common.puml\`.
- View-специфичные блоки можно класть в \`planning/<quarter>/gantt/preamble/quarter-plan.puml\`, \`commander-plan.puml\`, \`actual-progress.puml\`.
- Feature lanes на общем gantt должны идти отдельными секциями \`-- Название фичи --\`.
- Actual-progress include-файлы генерируются из \`planning/actualization.md\` и \`slices/*/execution/tasks.md\`.
- Не начатые execution tasks (\`Progress % = 0\`, нет actual dates) не рисуются в прошлом: при каждой генерации генератор сдвигает их на today/следующий рабочий день только в PlantUML.
- Внутри feature не начатый frontend стартует не раньше чем через 3 рабочих дня после старта не начатого backend/API.
- Resource lanes канонические: \`A<N>\`, \`B<N>\`, \`F<N>\`, \`Q<N>\`; неизвестный ресурс с известной ролью — \`TBD_A\`, \`TBD_B\`, \`TBD_F\`, \`TBD_Q\`.
- Состав команды и допустимые lanes лежат в \`.workflow/team.md\`.
- Не начатые задачи раскладываются без перегруза ресурса выше 100% в один рабочий день; пустой/\`TBD_*\`/неростерный executor назначается автоматически по роли или префиксу задачи.
EOF2

cp "$ROOT_DIR/templates/workflow/command-catalog.template.md" "$TARGET/.workflow/command-catalog.md"
cp "$ROOT_DIR/templates/workflow/command-cheatsheet.template.md" "$TARGET/.workflow/command-cheatsheet.md"
cp "$ROOT_DIR/templates/workflow/consistency-backlog.template.md" "$TARGET/.workflow/consistency-backlog.md"
cp "$ROOT_DIR/templates/workflow/team.template.md" "$TARGET/.workflow/team.md"

cat > "$TARGET/baseline/current/VERSION.md" <<EOF2
# Baseline Version

Version: initial
Date: $(date +%F)
Source release: initial
Previous baseline: none

## What this baseline represents

Initial scaffold baseline. Replace placeholders with the current deployed system description.
EOF2

cat > "$TARGET/baseline/current/domain/README.md" <<'EOF2'
# Domain Baseline

This directory is the canonical current-state domain model for the deployed system.

## Core files
- \`ubiquitous-language.md\`
- \`bounded-contexts.md\`
- \`aggregates.md\`
- \`business-rules.md\`
- \`state-machines/README.md\`
EOF2

cat > "$TARGET/baseline/current/domain/ubiquitous-language.md" <<'EOF2'
# Ubiquitous Language

Fill in the business terms used consistently across planning, requirements, prototypes and delivery.
EOF2

cat > "$TARGET/baseline/current/domain/bounded-contexts.md" <<'EOF2'
# Bounded Contexts

Describe the stable DDD decomposition of the current deployed system.
EOF2

cat > "$TARGET/baseline/current/domain/aggregates.md" <<'EOF2'
# Aggregates

List canonical aggregates, invariants and relationships of the current deployed system.
EOF2

cat > "$TARGET/baseline/current/domain/business-rules.md" <<'EOF2'
# Business Rules

Capture the stable cross-feature business rules of the current deployed system.
EOF2

cat > "$TARGET/baseline/current/domain/state-machines/README.md" <<'EOF2'
# State Machines

Describe canonical lifecycle states and transitions for deployed aggregates and versions.
EOF2

cat > "$TARGET/baseline/current/requirements/README.md" <<'EOF2'
# Canonical Requirements

Store release-promoted current-state requirements here.
EOF2

cat > "$TARGET/baseline/current/api/README.md" <<'EOF2'
# Canonical API

Store current-state API contracts and OpenAPI references here.
EOF2

cat > "$TARGET/baseline/current/ui/README.md" <<'EOF2'
# Canonical UI

Store current-state UI structure, navigation and component notes here.
EOF2

cat > "$TARGET/baseline/current/data/README.md" <<'EOF2'
# Canonical Data Model

Store current-state persistence and integration data model notes here.
EOF2

cat > "$TARGET/baseline/current/decisions/README.md" <<'EOF2'
# Decisions

Store ADR-style decisions that explain why the current baseline looks the way it does.
EOF2

cat > "$TARGET/releases/README.md" <<'EOF2'
# Releases

Each delivered release gets its own folder with final requirements and promotion notes before updating \`baseline/current\`.
EOF2

cat > "$TARGET/planning/intake/README.md" <<'EOF2'
# Feature Intake

Store feature preflight notes here before creating a new \`features/<slug>/\` structure.

- One markdown file per candidate feature.
- Use `.workflow/templates/intake/feature-intake.template.md`.
- Do not scaffold a new feature until the intake result is reviewed.
EOF2

echo "Project scaffold created at $TARGET"
