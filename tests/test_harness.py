from __future__ import annotations

import json
import hashlib
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

    def test_scaffold_contains_per_item_developer_handoff_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            contract = project / ".workflow/developer-handoff.md"
            receipt = project / ".workflow/templates/handoff/developer-receipt.template.json"
            manifest = project / ".workflow/templates/handoff/developer-manifest.template.json"
            self.assertTrue(contract.exists())
            self.assertTrue(receipt.exists())
            self.assertTrue(manifest.exists())
            self.assertIn("implemented-with-deviation", contract.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(receipt.read_text(encoding="utf-8"))["schema_version"], 3)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["reconciliation_policy"]["mode"], "per-item-continuation")

    def test_handoff_validator_accepts_per_item_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "package"
            package.mkdir()
            request = package / "request.md"
            request.write_text("# Request\n\nREQ-DEMO-001\n\nSCN-DEMO-001\n", encoding="utf-8")
            request_hash = hashlib.sha256(request.read_bytes()).hexdigest()
            receipt = {
                "schema_version": 3,
                "package_id": "demo",
                "package_revision": 1,
                "request_id": "demo",
                "request_version": 1,
                "request_sha256": request_hash,
                "status": "pending",
                "allowed_statuses": ["pending", "no-change-required", "proposal-created", "proposal-created-with-blocked-items", "blocked", "rejected-package"],
                "allowed_coverage_statuses": ["pending", "implemented-as-required", "implemented-with-deviation", "partially-implemented", "not-implemented", "blocked-product-decision", "blocked-dependency", "not-applicable"],
                "allowed_actions": ["pending", "no-change", "include-in-proposal", "return-product-question", "wait-for-dependency", "not-applicable"],
                "requirement_coverage": [{"requirement": "REQ-DEMO-001", "status": "pending", "action": "pending"}],
                "scenario_coverage": [{"scenario": "SCN-DEMO-001", "status": "pending", "action": "pending"}],
                "remaining_delta": [],
                "baseline_feedback": [],
                "requirements_feedback": [],
            }
            receipt_path = package / "receipt.template.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            manifest = {
                "schema_version": 5,
                "package_id": "demo",
                "package_revision": 1,
                "request": {"id": "demo", "version": 1},
                "payload": [
                    {"path": "request.md", "sha256": request_hash},
                    {"path": "receipt.template.json", "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()},
                ],
                "requirements": ["REQ-DEMO-001"],
                "scenarios": ["SCN-DEMO-001"],
                "reconciliation_policy": {"mode": "per-item-continuation"},
                "allowed_package_statuses": receipt["allowed_statuses"],
                "allowed_coverage_statuses": receipt["allowed_coverage_statuses"],
                "allowed_actions": receipt["allowed_actions"],
            }
            (package / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = run(sys.executable, str(ROOT / "scripts/validate-handoff.py"), str(package))
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

    def test_language_check_ignores_code_and_rejects_prose_anglicism(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = self.scaffold(Path(temp))
            requirements = project / "features/demo/requirements.md"
            requirements.parent.mkdir(parents=True)
            requirements.write_text("# Требования\n\nScope работ. Код: `scope`.\n", encoding="utf-8")
            result = run(
                sys.executable,
                str(project / ".workflow/tools/validate-language.py"),
                str(project),
                "--all",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout.count("'scope'"), 1)

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
