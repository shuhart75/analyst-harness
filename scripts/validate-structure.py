#!/usr/bin/env python3
from pathlib import Path
import sys

required = [
    ".workflow/llm-contract.md",
    ".workflow/agent-delegation.md",
    ".workflow/skills-policy.md",
    ".workflow/tooling-policy.md",
    ".workflow/tools/switch-mode.sh",
    ".workflow/tools/start-session.sh",
    ".workflow/tools/validate-structure.py",
    ".workflow/tools/validate-links.py",
    ".workflow/tools/sync-quarter-gantt.py",
    ".workflow/tools/sync-actual-progress-overlay.py",
    ".workflow/command-catalog.md",
    ".workflow/command-cheatsheet.md",
    ".workflow/consistency-backlog.md",
    ".workflow/active-mode.md",
    ".workflow/modes/planning.md",
    ".workflow/modes/requirements.md",
    ".workflow/modes/scope-prototype.md",
    ".workflow/modes/delivery-prototype.md",
    ".workflow/modes/execution-update.md",
    ".workflow/modes/release-finalization.md",
    ".workflow/templates/requirements/README.md",
    ".workflow/templates/requirements/slice.template.md",
    ".workflow/templates/requirements/frontend.template.md",
    ".workflow/templates/requirements/backend.template.md",
    ".workflow/templates/intake/README.md",
    ".workflow/templates/intake/feature-intake.template.md",
    "baseline/current/VERSION.md",
    "baseline/current/domain",
    "baseline/current/requirements",
    "baseline/current/api",
    "baseline/current/ui",
    "baseline/current/data",
    "baseline/versions",
    "planning/intake",
    "releases",
    "context/source-materials/current-system/requirements",
    "context/source-materials/current-system/screenshots",
    "context/source-materials/change-requests",
    "features",
]

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
missing = [p for p in required if not (root / p).exists()]
if missing:
    print("Missing required paths:")
    for item in missing:
        print(f"- {item}")
    sys.exit(1)
print("Structure OK")
