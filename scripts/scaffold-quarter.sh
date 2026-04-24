#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <project-root> <quarter-id>"
  exit 1
fi

PROJECT_ROOT="$1"
QUARTER="$2"
QUARTER_DIR="$PROJECT_ROOT/planning/$QUARTER"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$QUARTER_DIR/quarter" \
  "$QUARTER_DIR/gantt/preamble" \
  "$QUARTER_DIR/gantt/includes/quarter-plan" \
  "$QUARTER_DIR/gantt/includes/commander-plan" \
  "$QUARTER_DIR/gantt/includes/actual-progress"

cat > "$QUARTER_DIR/quarter/README.md" <<EOF2
# $QUARTER

## Notes

## Scope Decisions

## Comparison Notes
EOF2

cat > "$QUARTER_DIR/gantt/closed-days.txt" <<EOF2
# One date per line. Format: YYYY/MM/DD
# Example:
# 2026/05/01
EOF2

cat > "$QUARTER_DIR/gantt/preamble/common.puml" <<EOF2
' Add team calendar blocks, shared milestones, or external dependency notes here.
EOF2

python3 "$ROOT_DIR/scripts/sync-quarter-gantt.py" "$QUARTER_DIR/gantt"

echo "Quarter scaffold created at $QUARTER_DIR"
