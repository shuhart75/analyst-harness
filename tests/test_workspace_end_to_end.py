from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)


class AnalystWorkspaceEndToEndTests(unittest.TestCase):
    def initialize(self, repository: Path, remote_url: str | None = None) -> str:
        self.assertEqual(run("git", "init", "-b", "main", str(repository)).returncode, 0)
        self.assertEqual(run("git", "-C", str(repository), "config", "user.name", "Harness Test").returncode, 0)
        self.assertEqual(run("git", "-C", str(repository), "config", "user.email", "harness@example.test").returncode, 0)
        if remote_url:
            self.assertEqual(run("git", "-C", str(repository), "remote", "add", "origin", remote_url).returncode, 0)
        self.assertEqual(run("git", "-C", str(repository), "add", "-A").returncode, 0)
        committed = run("git", "-C", str(repository), "commit", "-m", "initial")
        self.assertEqual(committed.returncode, 0, committed.stdout + committed.stderr)
        return run("git", "-C", str(repository), "rev-parse", "HEAD").stdout.strip()

    def test_real_clone_uses_named_roles_from_root_and_analytics_identically(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            analytical_work = root / "analytical-work"
            scaffold = run("bash", str(ROOT / "scripts/scaffold-project.sh"), str(analytical_work))
            self.assertEqual(scaffold.returncode, 0, scaffold.stdout + scaffold.stderr)
            self.initialize(analytical_work)
            analytical_remote = root / "knowledge.git"
            self.assertEqual(run("git", "clone", "--bare", str(analytical_work), str(analytical_remote)).returncode, 0)

            code_work = root / "code-work"
            (code_work / "backend").mkdir(parents=True)
            (code_work / "frontend").mkdir()
            (code_work / "backend/AGENTS.md").write_text("# Backend SDD\n", encoding="utf-8")
            (code_work / "frontend/AGENTS.md").write_text("# Frontend SDD\n", encoding="utf-8")
            (code_work / "backend/Registry.java").write_text("class Registry { String productCode; }\n", encoding="utf-8")
            (code_work / "frontend/Registry.tsx").write_text("export const Registry = () => null;\n", encoding="utf-8")
            code_head = self.initialize(code_work)
            code_remote = root / "application.git"
            self.assertEqual(run("git", "clone", "--bare", str(code_work), str(code_remote)).returncode, 0)

            harness = root / "analyst-harness"
            cloned_harness = run("git", "clone", "--no-local", str(ROOT), str(harness))
            self.assertEqual(cloned_harness.returncode, 0, cloned_harness.stdout + cloned_harness.stderr)
            working_diff = run("git", "diff", "--binary", "HEAD", cwd=ROOT).stdout
            if working_diff:
                applied = subprocess.run(
                    ("git", "apply"), cwd=harness, input=working_diff, text=True, capture_output=True, check=False
                )
                self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            untracked = run("git", "ls-files", "--others", "--exclude-standard", cwd=ROOT)
            self.assertEqual(untracked.returncode, 0, untracked.stdout + untracked.stderr)
            for relative in untracked.stdout.splitlines():
                source = ROOT / relative
                target = harness / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            harness_status_before = run("git", "status", "--porcelain=v1", cwd=harness).stdout
            configured = run(
                sys.executable,
                "scripts/workspace.py",
                "configure",
                "--analytical-mode",
                "clone",
                "--analytical-url",
                str(analytical_remote),
                "--analytical-dir",
                "knowledge",
                "--code-mode",
                "clone",
                "--code-url",
                str(code_remote),
                "--code-dir",
                "application",
                cwd=harness,
            )
            self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
            bootstrap = run(sys.executable, "scripts/workspace.py", "bootstrap", cwd=harness)
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stdout + bootstrap.stderr)
            analytics = harness / "knowledge"
            code = harness / "application"
            entrypoint_text = (analytics / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("analyst-harness-local-entrypoint:v1", entrypoint_text)
            self.assertIn(f"HARNESS_ROOT = {harness}", entrypoint_text)
            self.assertIn(f"PROJECT_ROOT = {analytics}", entrypoint_text)
            self.assertIn(f"CODE_ROOT = {code}", entrypoint_text)
            self.assertEqual(run("git", "check-ignore", "AGENTS.md", cwd=analytics).returncode, 0)
            self.assertEqual(run("git", "check-ignore", ".idea/modules.xml", cwd=analytics).returncode, 0)
            self.assertEqual(run("git", "check-ignore", ".gigacode/settings.json", cwd=analytics).returncode, 0)
            self.assertEqual(run("git", "status", "--porcelain=v1", cwd=analytics).stdout, "")

            root_project = run(sys.executable, "scripts/workspace.py", "project-root", cwd=harness)
            analytics_project = run(
                sys.executable,
                "../scripts/workspace.py",
                "--root",
                "..",
                "project-root",
                cwd=analytics,
            )
            self.assertEqual(root_project.returncode, 0, root_project.stdout + root_project.stderr)
            self.assertEqual(analytics_project.returncode, 0, analytics_project.stdout + analytics_project.stderr)
            self.assertEqual(root_project.stdout.strip(), analytics_project.stdout.strip())

            root_code = run(sys.executable, "scripts/code-inspect.py", "doctor", "knowledge", cwd=harness)
            analytics_code = run(sys.executable, "../scripts/code-inspect.py", "doctor", ".", cwd=analytics)
            self.assertEqual(root_code.returncode, 0, root_code.stdout + root_code.stderr)
            self.assertEqual(analytics_code.returncode, 0, analytics_code.stdout + analytics_code.stderr)
            self.assertEqual(json.loads(root_code.stdout), json.loads(analytics_code.stdout))
            root_locate = run(
                sys.executable,
                "scripts/code-inspect.py",
                "locate",
                "knowledge",
                "productCode",
                "--contour",
                "backend",
                cwd=harness,
            )
            analytics_locate = run(
                sys.executable,
                "../scripts/code-inspect.py",
                "locate",
                ".",
                "productCode",
                "--contour",
                "backend",
                cwd=analytics,
            )
            self.assertEqual(root_locate.returncode, 0, root_locate.stdout + root_locate.stderr)
            self.assertEqual(analytics_locate.returncode, 0, analytics_locate.stdout + analytics_locate.stderr)
            self.assertEqual(json.loads(root_locate.stdout), json.loads(analytics_locate.stdout))
            inspection_environment = {**os.environ, "XDG_STATE_HOME": str(root / "inspection-state")}
            for cwd, tool, project in (
                (harness, "scripts/code-inspect.py", "knowledge"),
                (analytics, "../scripts/code-inspect.py", "."),
            ):
                begun = run(
                    sys.executable,
                    tool,
                    "begin",
                    project,
                    "--contour",
                    "backend",
                    "--query",
                    "productCode",
                    cwd=cwd,
                    env=inspection_environment,
                )
                self.assertEqual(begun.returncode, 0, begun.stdout + begun.stderr)
                state_path = begun.stdout.splitlines()[0]
                verified = run(sys.executable, tool, "verify", state_path, cwd=cwd, env=inspection_environment)
                self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
                self.assertEqual(json.loads(verified.stdout)["result"], "unchanged")

            root_doctor = run(sys.executable, "scripts/harnessctl.py", "doctor", "knowledge", cwd=harness)
            analytics_doctor = run(sys.executable, "../scripts/harnessctl.py", "doctor", ".", cwd=analytics)
            self.assertEqual(root_doctor.returncode, 0, root_doctor.stdout + root_doctor.stderr)
            self.assertEqual(analytics_doctor.returncode, 0, analytics_doctor.stdout + analytics_doctor.stderr)

            root_feature = run("bash", "scripts/scaffold-feature.sh", "knowledge", "from-root", cwd=harness)
            analytics_feature = run("bash", "../scripts/scaffold-feature.sh", ".", "from-analytics", cwd=analytics)
            self.assertEqual(root_feature.returncode, 0, root_feature.stdout + root_feature.stderr)
            self.assertEqual(analytics_feature.returncode, 0, analytics_feature.stdout + analytics_feature.stderr)
            self.assertTrue((analytics / "features/from-root/feature.md").is_file())
            self.assertTrue((analytics / "features/from-analytics/feature.md").is_file())
            self.assertFalse((harness / "features").exists())
            self.assertEqual(run("git", "rev-parse", "HEAD", cwd=code).stdout.strip(), code_head)
            self.assertEqual(run("git", "status", "--porcelain=v1", cwd=code).stdout, "")
            self.assertEqual(run("git", "status", "--porcelain=v1", cwd=harness).stdout, harness_status_before)


if __name__ == "__main__":
    unittest.main()
