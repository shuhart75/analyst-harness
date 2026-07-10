from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


class HarnessTests(unittest.TestCase):
    def scaffold(self, root: Path) -> Path:
        project = root / "project"
        result = run("bash", str(ROOT / "scripts/scaffold-project.sh"), str(project))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return project

    def test_clean_scaffold_passes_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            result = run(sys.executable, str(project / ".workflow/tools/harnessctl.py"), "doctor", str(project))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_active_mode_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            active = project / ".workflow/active-mode.md"
            active.write_text(active.read_text(encoding="utf-8").replace("modes/planning.md", "modes/requirements.md"), encoding="utf-8")
            result = run(sys.executable, str(project / ".workflow/tools/validate-workflow.py"), str(project))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("active mode mismatch", result.stdout)

    def test_feature_scaffold_does_not_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            result = run("bash", str(ROOT / "scripts/scaffold-feature.sh"), str(project), "demo")
            self.assertEqual(result.returncode, 0)
            feature = project / "features/demo/feature.md"
            feature.write_text("USER CONTENT\n", encoding="utf-8")
            result = run("bash", str(ROOT / "scripts/scaffold-feature.sh"), str(project), "demo")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(feature.read_text(encoding="utf-8"), "USER CONTENT\n")

    def test_project_merge_does_not_add_knowledge_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "existing"
            (project / "baseline/current/domain").mkdir(parents=True)
            result = run("bash", str(ROOT / "scripts/scaffold-project.sh"), str(project), "--merge")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / ".workflow/tools/harnessctl.py").exists())
            self.assertFalse((project / "baseline/current/domain/aggregates.md").exists())

    def test_run_escalates_after_iteration_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            result = run(
                sys.executable,
                str(project / ".workflow/tools/harnessctl.py"),
                "run-init",
                str(project),
                "planning",
                "--run-id",
                "test-run",
                "--max-iterations",
                "2",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_file = project / ".workflow/runs/test-run/run.json"
            for _ in range(2):
                result = run(sys.executable, str(project / ".workflow/tools/harnessctl.py"), "run-advance", str(run_file), "fail")
                self.assertEqual(result.returncode, 0)
            payload = json.loads(run_file.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "escalated")

    def test_approved_plan_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            result = run("bash", str(ROOT / "scripts/scaffold-quarter.sh"), str(project), "2026-Q3")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(
                sys.executable,
                str(project / ".workflow/tools/harnessctl.py"),
                "plan-approve",
                str(project),
                "2026-Q3",
                "--by",
                "owner",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = project / "planning/2026-Q3/plan-state.md"
            self.assertIn("## Immutability", state.read_text(encoding="utf-8"))
            quarter_plan = project / "planning/2026-Q3/gantt/quarter-plan.puml"
            quarter_plan.write_text(quarter_plan.read_text(encoding="utf-8") + "' tampered\n", encoding="utf-8")
            result = run(sys.executable, str(project / ".workflow/tools/validate-planning.py"), str(project))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("approved plan was modified", result.stdout)


if __name__ == "__main__":
    unittest.main()
