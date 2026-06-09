#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <project-root> <feature-slug>"
  exit 1
fi

PROJECT_ROOT="$1"
FEATURE="$2"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FEATURE_DIR="$PROJECT_ROOT/features/$FEATURE"

mkdir -p "$FEATURE_DIR/planning/stories" "$FEATURE_DIR/planning/scope-prototype" "$FEATURE_DIR/slices"
cp "$ROOT_DIR/templates/planning/feature.template.md" "$FEATURE_DIR/feature.md"
cp "$ROOT_DIR/templates/planning/estimates.template.md" "$FEATURE_DIR/planning/estimates.md"
cp "$ROOT_DIR/templates/planning/actualization.template.md" "$FEATURE_DIR/planning/actualization.md"
cp "$ROOT_DIR/templates/planning/planning-context.template.md" "$FEATURE_DIR/planning/planning-context.md"
cp "$ROOT_DIR/templates/planning/assumptions.template.md" "$FEATURE_DIR/planning/assumptions.md"
cp "$ROOT_DIR/templates/planning/risk-register.template.md" "$FEATURE_DIR/planning/risk-register.md"
cp "$ROOT_DIR/templates/planning/story-map.template.md" "$FEATURE_DIR/planning/story-map.md"
cp "$ROOT_DIR/templates/context/feature-context-summary.template.md" "$FEATURE_DIR/context-summary.md"
cp "$ROOT_DIR/templates/context/artifact-map.template.md" "$FEATURE_DIR/artifact-map.md"
cp "$ROOT_DIR/templates/domain/domain-impact.template.md" "$FEATURE_DIR/domain-impact.md"
cp "$ROOT_DIR/templates/prototypes/scope-prototype-notes.template.md" "$FEATURE_DIR/planning/scope-prototype/notes.md"
cp "$ROOT_DIR/templates/prototypes/prototype.html.template" "$FEATURE_DIR/planning/scope-prototype/prototype.html"
cat > "$FEATURE_DIR/references.md" <<EOF2
# References

- baseline/current/
- context/source-materials/current-system/requirements/
- context/source-materials/current-system/screenshots/
- context/source-materials/change-requests/
EOF2

echo "Feature scaffold created at $FEATURE_DIR"
