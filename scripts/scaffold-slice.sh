#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <project-root> <feature-slug> <slice-slug>"
  exit 1
fi

PROJECT_ROOT="$1"
FEATURE="$2"
SLICE="$3"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLICE_DIR="$PROJECT_ROOT/features/$FEATURE/slices/$SLICE"
PROJECT_TEMPLATE_DIR="$PROJECT_ROOT/.workflow/templates/requirements"

if [[ -d "$PROJECT_TEMPLATE_DIR" ]]; then
  REQUIREMENTS_TEMPLATE_DIR="$PROJECT_TEMPLATE_DIR"
else
  REQUIREMENTS_TEMPLATE_DIR="$ROOT_DIR/templates/requirements"
fi

mkdir -p "$SLICE_DIR/requirements" "$SLICE_DIR/delivery-prototype" "$SLICE_DIR/execution/tasks" "$SLICE_DIR/.research" "$SLICE_DIR/testing"
cp "$REQUIREMENTS_TEMPLATE_DIR/slice.template.md" "$SLICE_DIR/slice.md"
cp "$REQUIREMENTS_TEMPLATE_DIR/frontend.template.md" "$SLICE_DIR/requirements/frontend.md"
cp "$REQUIREMENTS_TEMPLATE_DIR/backend.template.md" "$SLICE_DIR/requirements/backend.md"
cp "$ROOT_DIR/templates/context/slice-context-summary.template.md" "$SLICE_DIR/context-summary.md"
cp "$ROOT_DIR/templates/handoff/slice-implementation-handoff.template.md" "$SLICE_DIR/implementation-handoff.md"
cp "$ROOT_DIR/templates/execution/implementation-plan.template.md" "$SLICE_DIR/execution/implementation-plan.md"
cp "$ROOT_DIR/templates/research/research-summary.template.md" "$SLICE_DIR/.research/summary.md"
cp "$ROOT_DIR/templates/testing/slice-test-plan.template.md" "$SLICE_DIR/testing/test-plan.md"
cp "$ROOT_DIR/templates/prototypes/delivery-prototype-notes.template.md" "$SLICE_DIR/delivery-prototype/notes.md"
cp "$ROOT_DIR/templates/prototypes/prototype.html.template" "$SLICE_DIR/delivery-prototype/prototype.html"
cp "$ROOT_DIR/templates/execution/tasks.template.md" "$SLICE_DIR/execution/tasks.md"

echo "Slice scaffold created at $SLICE_DIR"
