from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False, env=env)


class AnalystWorkspaceTests(unittest.TestCase):
    def create_remote(self, root: Path, name: str, files: dict[str, str]) -> Path:
        work = root / f"seed-{name}"
        remote = root / f"{name}.git"
        self.assertEqual(run("git", "init", "-b", "main", str(work)).returncode, 0)
        self.assertEqual(run("git", "-C", str(work), "config", "user.name", "Harness Test").returncode, 0)
        self.assertEqual(run("git", "-C", str(work), "config", "user.email", "harness@example.test").returncode, 0)
        for relative, content in files.items():
            path = work / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.assertEqual(run("git", "-C", str(work), "add", ".").returncode, 0)
        self.assertEqual(run("git", "-C", str(work), "commit", "-m", "initial").returncode, 0)
        self.assertEqual(run("git", "clone", "--bare", str(work), str(remote)).returncode, 0)
        return remote

    def test_clone_workspace_keeps_harness_outside_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            workspace.mkdir()
            analytical_remote = self.create_remote(root, "analytical", {"README.md": "# Проект\n"})
            code_remote = self.create_remote(root, "code", {
                "backend/AGENTS.md": "# Серверные правила\n",
                "backend/app.py": "VALUE = 1\n",
                "frontend/AGENTS.md": "# Клиентские правила\n",
            })
            env = {**os.environ, "ANALYST_HARNESS_STATE_ROOT": str(workspace / ".workspace-state")}
            configure = run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "configure",
                "--analytical-mode",
                "clone",
                "--analytical-url",
                str(analytical_remote),
                "--code-mode",
                "clone",
                "--code-url",
                str(code_remote),
                env=env,
            )
            self.assertEqual(configure.returncode, 0, configure.stdout + configure.stderr)
            bootstrap = run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "bootstrap",
                env=env,
            )
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stdout + bootstrap.stderr)
            analytical = workspace / "analytical-project"
            for forbidden in (".workflow", ".vscode", "AGENTS.md"):
                self.assertFalse((analytical / forbidden).exists())
            self.assertTrue((analytical / "planning/team.md").is_file())
            self.assertEqual(
                run("git", "-C", str(workspace / "code"), "remote", "get-url", "--push", "origin").stdout.strip(),
                "DISABLED_BY_ANALYST_HARNESS",
            )
            registry = json.loads((workspace / ".workspace-state/code-repos.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["repositories"][0]["id"], "code")
            self.assertEqual(registry["repositories"][0]["location"]["relative_to_analytical"], "../code")
            self.assertEqual(set(registry["repositories"][0]["contours"]), {"backend", "frontend"})
            multi_root = json.loads((workspace / "analyst-workspace.code-workspace").read_text(encoding="utf-8"))
            self.assertEqual([item["name"] for item in multi_root["folders"]], ["analyst-harness", "analytical", "code-read-only"])

    def test_create_workspace_can_skip_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "workspace"
            workspace.mkdir()
            env = {**os.environ, "ANALYST_HARNESS_STATE_ROOT": str(workspace / ".workspace-state")}
            configure = run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "configure",
                "--analytical-mode",
                "create",
                "--code-mode",
                "skip",
                env=env,
            )
            self.assertEqual(configure.returncode, 0, configure.stdout + configure.stderr)
            bootstrap = run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "bootstrap",
                env=env,
            )
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stdout + bootstrap.stderr)
            analytical = workspace / "analytical-project"
            self.assertEqual(run("git", "-C", str(analytical), "rev-parse", "--show-toplevel").stdout.strip(), str(analytical))
            registry = json.loads((workspace / ".workspace-state/code-repos.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["repositories"], [])
            doctor = run(sys.executable, str(ROOT / "scripts/code-inspect.py"), "doctor", str(analytical), env=env)
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)

    def test_embedded_harness_is_rejected_without_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            workspace.mkdir()
            remote = self.create_remote(root, "legacy", {
                "README.md": "# Проект\n",
                ".workflow/marker": "legacy\n",
            })
            env = {**os.environ, "ANALYST_HARNESS_STATE_ROOT": str(workspace / ".workspace-state")}
            self.assertEqual(run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "configure",
                "--analytical-mode",
                "clone",
                "--analytical-url",
                str(remote),
                "--code-mode",
                "skip",
                env=env,
            ).returncode, 0)
            bootstrap = run(
                sys.executable,
                str(ROOT / "scripts/workspace.py"),
                "--root",
                str(workspace),
                "bootstrap",
                env=env,
            )
            self.assertNotEqual(bootstrap.returncode, 0)
            self.assertIn("встроенную обвязку", bootstrap.stdout)
            self.assertTrue((workspace / "analytical-project/.workflow/marker").is_file())


if __name__ == "__main__":
    unittest.main()
