from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/reverse_patch.py"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False, env=env)


class ReversePatchTests(unittest.TestCase):
    def git(self, repository: Path, *args: str) -> str:
        result = run("git", "-C", str(repository), *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def identity(self, repository: Path) -> None:
        self.git(repository, "config", "user.name", "Harness Test")
        self.git(repository, "config", "user.email", "harness@example.test")

    def prepare(self, directory: Path, artifact_id: str = "20260821T120000000000Z") -> dict:
        seed = directory / "seed"
        remote = directory / "changeswork-copy.git"
        root = directory / "analyst-harness"
        repository = root / "analytical-project"
        target = directory / "documents"
        home = directory / "home"
        inbox = root / "reverse-patch-inbox"
        for path in (root, home, inbox):
            path.mkdir(parents=True)

        self.assertEqual(run("git", "init", "-b", "main", str(seed)).returncode, 0)
        self.identity(seed)
        (seed / "README.md").write_text("# Исходное состояние\n", encoding="utf-8")
        (seed / "features/example").mkdir(parents=True)
        (seed / "features/example/requirements.md").write_text("# Требования\n\nВерсия 1.\n", encoding="utf-8")
        self.git(seed, "add", "--", "README.md", "features/example/requirements.md")
        self.git(seed, "commit", "-m", "initial")
        self.assertEqual(run("git", "clone", "--bare", str(seed), str(remote)).returncode, 0)
        self.assertEqual(run("git", "clone", str(remote), str(repository)).returncode, 0)
        self.assertEqual(run("git", "clone", str(remote), str(target)).returncode, 0)
        self.identity(repository)
        self.identity(target)

        source_commit = self.git(repository, "rev-parse", "HEAD")
        source_tree = self.git(repository, "rev-parse", "HEAD^{tree}")
        (target / "features/example/requirements.md").write_text(
            "# Требования\n\nВерсия 2 после работы в documents.\n",
            encoding="utf-8",
        )
        (target / "features/example/notes.md").write_text("# Примечания\n", encoding="utf-8")
        self.git(target, "add", "--", "features/example/requirements.md", "features/example/notes.md")
        self.git(target, "commit", "-m", "update example requirements")
        analytics_commit = self.git(target, "rev-parse", "HEAD")
        analytics_tree = self.git(target, "rev-parse", "HEAD^{tree}")
        patch_result = run(
            "git", "-C", str(target), "diff", "--binary", "--full-index", "--no-renames",
            source_commit, analytics_commit, "--", ".",
        )
        self.assertEqual(patch_result.returncode, 0, patch_result.stderr)
        patch = inbox / f"reverse-diff-{artifact_id}.patch"
        patch.write_text(patch_result.stdout, encoding="utf-8")
        changed = run(
            "git", "-C", str(target), "diff", "--name-only", "-z",
            source_commit, analytics_commit, "--", ".",
        )
        self.assertEqual(changed.returncode, 0, changed.stderr)
        changed_paths = [item for item in changed.stdout.split("\0") if item]
        metadata = {
            "schema_version": 2,
            "artifact_id": artifact_id,
            "created_at": "2026-08-21T12:00:00+00:00",
            "source_repository": "changeswork-copy",
            "analytics_repository": "documents",
            "source_branch": "main",
            "analytics_branch": "main",
            "source_commit": source_commit,
            "analytics_commit": analytics_commit,
            "documents_commit": analytics_commit,
            "source_tree": source_tree,
            "analytics_tree": analytics_tree,
            "documents_tree": analytics_tree,
            "repositories_identical": False,
            "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
            "changed_path_count": len(changed_paths),
            "changed_paths": changed_paths,
            "included_features": ["example"],
            "included_analytics_commits": [
                {"commit": analytics_commit, "subject": "update example requirements"}
            ],
            "approved_source_deletions": [],
            "tree_verified": True,
            "content_policy_verified": True,
            "verified": True,
        }
        metadata_path = inbox / f"reverse-diff-{artifact_id}.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (root / ".analyst-workspace.json").write_text(
            json.dumps({
                "schema_version": 2,
                "analytical": {"mode": "clone", "path": "analytical-project", "remote_url": str(remote)},
                "code": {"mode": "skip", "path": None, "remote_url": None},
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        environment = {
            **os.environ,
            "HOME": str(home),
            "ANALYST_HARNESS_STATE_ROOT": str(root / ".workspace-state"),
        }
        return {
            "root": root,
            "repository": repository,
            "remote": remote,
            "target": target,
            "patch": patch,
            "metadata_path": metadata_path,
            "metadata": metadata,
            "env": environment,
        }

    def tool(self, fixture: dict, *arguments: str) -> subprocess.CompletedProcess[str]:
        return run(
            sys.executable,
            str(TOOL),
            "--root",
            str(fixture["root"]),
            *arguments,
            env=fixture["env"],
        )

    def receipt(self, fixture: dict) -> dict:
        artifact_id = fixture["metadata"]["artifact_id"]
        path = fixture["root"] / "reverse-patch-receipts" / f"reverse-diff-{artifact_id}.receipt.json"
        self.assertTrue(path.is_file())
        return json.loads(path.read_text(encoding="utf-8"))

    def assert_source_unchanged(self, fixture: dict) -> None:
        repository = fixture["repository"]
        self.assertEqual(self.git(repository, "rev-parse", "HEAD"), fixture["metadata"]["source_commit"])
        self.assertEqual(run("git", "-C", str(repository), "status", "--porcelain=v1").stdout, "")

    def test_apply_push_and_repeat_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            applied = self.tool(fixture, "apply")
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual(payload["status"], "applied-and-pushed")
            self.assertEqual(payload["result_tree"], fixture["metadata"]["analytics_tree"])
            self.assertEqual(
                self.git(fixture["remote"], "rev-parse", "refs/heads/main"),
                payload["result_commit"],
            )
            repeated = self.tool(fixture, "apply")
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already-applied")
            receipt = self.receipt(fixture)
            self.assertEqual(receipt["result_commit"], payload["result_commit"])
            self.assertEqual(receipt["result_tree"], fixture["metadata"]["analytics_tree"])

    def test_wrong_sha_is_blocked_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            fixture["metadata"]["patch_sha256"] = "0" * 64
            fixture["metadata_path"].write_text(
                json.dumps(fixture["metadata"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("проверенная обратная заплата не найдена", result.stdout)
            self.assert_source_unchanged(fixture)

    def test_advanced_source_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            publisher = Path(temp) / "publisher"
            self.assertEqual(run("git", "clone", str(fixture["remote"]), str(publisher)).returncode, 0)
            self.identity(publisher)
            (publisher / "README.md").write_text("# Source advanced\n", encoding="utf-8")
            self.git(publisher, "add", "--", "README.md")
            self.git(publisher, "commit", "-m", "advance source")
            self.git(publisher, "push", "origin", "main")
            advanced = self.git(publisher, "rev-parse", "HEAD")
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("не совпадает с исходным коммитом", result.stdout)
            self.assertEqual(self.git(fixture["repository"], "rev-parse", "HEAD"), advanced)
            self.assertEqual(run("git", "-C", str(fixture["repository"]), "status", "--porcelain=v1").stdout, "")

    def test_target_tree_mismatch_is_blocked_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            fixture["metadata"]["analytics_tree"] = "a" * 40
            fixture["metadata"]["documents_tree"] = "a" * 40
            fixture["metadata_path"].write_text(
                json.dumps(fixture["metadata"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("не воспроизводит целевое дерево", result.stdout)
            self.assert_source_unchanged(fixture)

    def test_changed_path_mismatch_rolls_back_applied_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            fixture["metadata"]["changed_paths"] = ["features/example/requirements.md"]
            fixture["metadata"]["changed_path_count"] = 1
            fixture["metadata_path"].write_text(
                json.dumps(fixture["metadata"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Состав применённых путей не совпадает", result.stdout)
            self.assert_source_unchanged(fixture)

    def test_dirty_worktree_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            (fixture["repository"] / "local.txt").write_text("local\n", encoding="utf-8")
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("содержит локальные изменения", result.stdout)
            self.assertEqual(self.git(fixture["repository"], "rev-parse", "HEAD"), fixture["metadata"]["source_commit"])

    def test_multiple_candidates_require_artifact_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            second_id = "20260821T130000000000Z"
            second_patch = fixture["patch"].with_name(f"reverse-diff-{second_id}.patch")
            shutil.copyfile(fixture["patch"], second_patch)
            second_metadata = {**fixture["metadata"], "artifact_id": second_id}
            second_metadata_path = fixture["metadata_path"].with_name(f"reverse-diff-{second_id}.json")
            second_metadata_path.write_text(
                json.dumps(second_metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("укажи artifact_id", result.stdout)
            selected = self.tool(fixture, "apply", "--artifact-id", fixture["metadata"]["artifact_id"])
            self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)

    def test_legacy_schema_two_metadata_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            for key in ("source_branch", "analytics_branch", "included_features", "included_analytics_commits"):
                fixture["metadata"].pop(key)
            fixture["metadata_path"].write_text(
                json.dumps(fixture["metadata"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.tool(fixture, "apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "applied-and-pushed")

    def test_failed_push_is_retried_without_second_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = self.prepare(Path(temp))
            hook = fixture["remote"] / "hooks/pre-receive"
            hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
            first = self.tool(fixture, "apply")
            self.assertNotEqual(first.returncode, 0)
            self.assertIn("создан, но отправка не выполнена", first.stdout)
            first_commit = self.git(fixture["repository"], "rev-parse", "HEAD")
            self.assertEqual(self.receipt(fixture)["status"], "committed-not-pushed")
            hook.unlink()
            second = self.tool(fixture, "apply")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            payload = json.loads(second.stdout)
            self.assertEqual(payload["result_commit"], first_commit)
            self.assertEqual(payload["status"], "applied-and-pushed")
            self.assertEqual(self.git(fixture["repository"], "rev-list", "--count", "main"), "2")


if __name__ == "__main__":
    unittest.main()
