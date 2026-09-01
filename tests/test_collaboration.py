from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "scripts/workspace.py"
COLLABORATION = ROOT / "scripts/collaboration.py"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False, env=env)


class CollaborationTests(unittest.TestCase):
    def git(self, repository: Path, *args: str) -> str:
        result = run("git", "-C", str(repository), *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def prepare_workspace(self, root: Path) -> tuple[Path, Path, Path, dict[str, str]]:
        seed = root / "seed"
        remote = root / "analytics.git"
        workspace = root / "harness"
        seed.mkdir()
        workspace.mkdir()
        self.assertEqual(run("git", "init", "-b", "main", str(seed)).returncode, 0)
        self.git(seed, "config", "user.name", "Harness Test")
        self.git(seed, "config", "user.email", "harness@example.test")
        feature = seed / "features/registry"
        feature.mkdir(parents=True)
        (feature / "requirements.md").write_text("# Требования\n\nИсходная версия.\n", encoding="utf-8")
        self.git(seed, "add", "--", "features/registry/requirements.md")
        self.git(seed, "commit", "-m", "Добавить требования")
        self.assertEqual(run("git", "clone", "--bare", str(seed), str(remote)).returncode, 0)
        self.git(remote, "symbolic-ref", "HEAD", "refs/heads/main")

        environment = {
            **os.environ,
            "ANALYST_HARNESS_STATE_ROOT": str(workspace / ".workspace-state"),
        }
        configured = run(
            sys.executable,
            str(WORKSPACE),
            "--root",
            str(workspace),
            "configure",
            "--analytical-mode",
            "clone",
            "--analytical-url",
            str(remote),
            "--preserve-analytical-tree",
            "--code-mode",
            "skip",
            env=environment,
        )
        self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
        bootstrapped = run(
            sys.executable,
            str(WORKSPACE),
            "--root",
            str(workspace),
            "bootstrap",
            env=environment,
        )
        self.assertEqual(bootstrapped.returncode, 0, bootstrapped.stdout + bootstrapped.stderr)
        analytics = workspace / "analytical-project"
        self.git(analytics, "config", "user.name", "Harness Test")
        self.git(analytics, "config", "user.email", "harness@example.test")
        return workspace, analytics, remote, environment

    def collaboration(
        self,
        workspace: Path,
        environment: dict[str, str],
        command: str,
        *arguments: str,
        expected: int = 0,
    ) -> dict:
        result = run(
            sys.executable,
            str(COLLABORATION),
            "--root",
            str(workspace),
            command,
            *arguments,
            env=environment,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_complete_feature_branch_cycle_and_delivery_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace, analytics, remote, environment = self.prepare_workspace(root)
            initial = self.collaboration(workspace, environment, "status")
            self.assertEqual(initial["status"], "migration-required")
            blocked = self.collaboration(
                workspace,
                environment,
                "require-main-for-delivery",
                "--feature",
                "registry",
                expected=2,
            )
            self.assertEqual(blocked["reason"], "collaboration-migration-required")

            migrated = self.collaboration(
                workspace, environment, "migrate", "--analyst", "ivan"
            )
            self.assertEqual(migrated["status"], "migrated-clean")
            started = self.collaboration(
                workspace, environment, "start", "--feature", "registry"
            )
            branch = started["branch"]
            self.assertEqual(branch, "feature/registry/ivan")
            main_before = self.git(remote, "rev-parse", "main")

            requirements = "features/registry/requirements.md"
            (analytics / requirements).write_text(
                "# Требования\n\nРабочая версия аналитика.\n",
                encoding="utf-8",
            )
            before_blocked_save = self.git(analytics, "rev-parse", "HEAD")
            blocked_save = run(
                sys.executable,
                str(COLLABORATION),
                "--root",
                str(workspace),
                "save",
                "--message",
                "Уточнить RSCON-123",
                "--path",
                requirements,
                env=environment,
            )
            self.assertNotEqual(blocked_save.returncode, 0)
            self.assertIn("Сообщение коммита отклонено", blocked_save.stdout)
            self.assertEqual(self.git(analytics, "rev-parse", "HEAD"), before_blocked_save)
            self.assertEqual(self.git(analytics, "diff", "--cached", "--name-only"), "")
            saved = self.collaboration(
                workspace,
                environment,
                "save",
                "--message",
                "Уточнить требования Реестра",
                "--path",
                requirements,
            )
            self.assertTrue(saved["pushed"])
            self.assertEqual(self.git(remote, "rev-parse", "main"), main_before)

            submitted = self.collaboration(workspace, environment, "submit")
            self.assertFalse(submitted["merge_request_created"])
            self.assertFalse(submitted["package_created"])
            self.assertIn("не создан", submitted["message"])
            premature = run(
                sys.executable,
                str(COLLABORATION),
                "--root",
                str(workspace),
                "require-main-for-delivery",
                "--feature",
                "registry",
                env=environment,
            )
            self.assertNotEqual(premature.returncode, 0)
            self.assertIn("незавершённая рабочая ветка", premature.stdout)

            integrator = root / "integrator"
            self.assertEqual(run("git", "clone", str(remote), str(integrator)).returncode, 0)
            self.git(integrator, "config", "user.name", "Integrator")
            self.git(integrator, "config", "user.email", "integrator@example.test")
            self.git(integrator, "fetch", "origin", branch)
            self.git(integrator, "merge", "--no-ff", f"origin/{branch}", "-m", "Принять требования")
            self.git(integrator, "push", "origin", "main")

            finished = self.collaboration(workspace, environment, "finish")
            self.assertEqual(finished["status"], "feature-work-finished")
            self.assertEqual(self.git(analytics, "branch", "--show-current"), "main")
            allowed = self.collaboration(
                workspace,
                environment,
                "require-main-for-delivery",
                "--feature",
                "registry",
            )
            self.assertTrue(allowed["delivery_allowed"])

            entrypoint = (analytics / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(f"HARNESS_ROOT = {workspace}", entrypoint)
            self.assertIn("HARNESS_ROOT/scripts/collaboration.py status", entrypoint)
            self.assertIn("feature/<feature>/<analyst>", entrypoint)

            restarted = self.collaboration(
                workspace, environment, "start", "--feature", "registry"
            )
            self.assertEqual(restarted["branch"], "feature/registry/ivan-2")
            self.assertEqual(
                self.git(analytics, "rev-parse", "HEAD"),
                self.git(remote, "rev-parse", "main"),
            )

    def test_migration_preserves_dirty_requirements_in_feature_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace, analytics, _, environment = self.prepare_workspace(Path(temporary))
            requirements = analytics / "features/registry/requirements.md"
            requirements.write_text("# Требования\n\nНесохранённая версия.\n", encoding="utf-8")
            needs_feature = self.collaboration(
                workspace,
                environment,
                "migrate",
                "--analyst",
                "ivan",
                expected=2,
            )
            self.assertEqual(needs_feature["status"], "feature-required")
            migrated = self.collaboration(
                workspace,
                environment,
                "migrate",
                "--analyst",
                "ivan",
                "--feature",
                "registry",
            )
            self.assertEqual(migrated["status"], "migrated-work-preserved")
            self.assertFalse(migrated["automatic_commit_created"])
            self.assertFalse(migrated["automatic_push_performed"])
            self.assertEqual(self.git(analytics, "branch", "--show-current"), "feature/registry/ivan")
            self.assertIn("Несохранённая версия", requirements.read_text(encoding="utf-8"))

    def test_conflicting_main_update_is_archived_and_aborted_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace, analytics, remote, environment = self.prepare_workspace(root)
            self.collaboration(workspace, environment, "migrate", "--analyst", "ivan")
            self.collaboration(workspace, environment, "start", "--feature", "registry")
            relative = "features/registry/requirements.md"
            requirements = analytics / relative
            requirements.write_text("# Требования\n\nВерсия аналитика.\n", encoding="utf-8")
            self.collaboration(
                workspace,
                environment,
                "save",
                "--message",
                "Изменить требования в рабочей ветке",
                "--path",
                relative,
            )

            colleague = root / "colleague"
            self.assertEqual(run("git", "clone", str(remote), str(colleague)).returncode, 0)
            self.git(colleague, "config", "user.name", "Colleague")
            self.git(colleague, "config", "user.email", "colleague@example.test")
            (colleague / relative).write_text("# Требования\n\nВерсия коллеги.\n", encoding="utf-8")
            self.git(colleague, "add", "--", relative)
            self.git(colleague, "commit", "-m", "Изменить требования в main")
            self.git(colleague, "push", "origin", "main")

            updated = run(
                sys.executable,
                str(COLLABORATION),
                "--root",
                str(workspace),
                "update",
                env=environment,
            )
            self.assertNotEqual(updated.returncode, 0)
            self.assertIn("feature-main-merge-conflict", updated.stdout)
            self.assertEqual(self.git(analytics, "branch", "--show-current"), "feature/registry/ivan")
            self.assertEqual(self.git(analytics, "status", "--porcelain=v1"), "")
            self.assertIn("Версия аналитика", requirements.read_text(encoding="utf-8"))

            snapshots = list((workspace / ".workspace-state/analytics-snapshots").glob("*/snapshot.json"))
            self.assertEqual(len(snapshots), 1)
            metadata = json.loads(snapshots[0].read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "conflict")
            self.assertEqual([item["path"] for item in metadata["conflicts"]], [relative])
            archived = metadata["conflicts"][0]["archived_files"]
            self.assertEqual(set(archived), {"base", "local", "incoming"})
            self.assertIn("Версия аналитика", Path(archived["local"]).read_text(encoding="utf-8"))
            self.assertIn("Версия коллеги", Path(archived["incoming"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
