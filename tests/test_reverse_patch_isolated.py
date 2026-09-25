from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_reverse_patch as existing


class IsolatedReversePatchTests(unittest.TestCase):
    git = existing.ReversePatchTests.git
    identity = existing.ReversePatchTests.identity
    prepare = existing.ReversePatchTests.prepare
    tool = existing.ReversePatchTests.tool
    receipt = existing.ReversePatchTests.receipt

    def active_fixture(self, directory, **kwargs):
        fixture = self.prepare(directory, **kwargs)
        repository = fixture["repository"]
        self.git(repository, "switch", "-c", "feature/example/analyst")
        (repository / "README.md").write_text("Active unfinished feature\n")
        self.git(repository, "add", "--", "README.md")
        self.git(repository, "commit", "-m", "Continue feature work")
        state = fixture["root"] / ".workspace-state"
        state.mkdir()
        (state / "workspace.json").write_text("{}\n")
        (state / "active-mode.md").write_text("mode: requirements\n")
        (state / "collaboration.json").write_text(json.dumps({
            "schema_version": 1, "mode": "multi-user-branches",
            "active_work": {"feature": "example", "branch": "feature/example/analyst", "status": "active"},
        }))
        return fixture

    def snapshot(self, fixture):
        repository = fixture["repository"]
        result = {path.relative_to(repository).as_posix(): path.read_bytes()
                  for path in repository.rglob("*") if path.is_file()}
        for name in ("collaboration.json", "workspace.json", "active-mode.md"):
            result["state/" + name] = (fixture["root"] / ".workspace-state" / name).read_bytes()
        return result

    def clone_path(self, fixture):
        return fixture["root"] / ".workspace-state/reverse-patch-clones" / fixture["metadata"]["artifact_id"]

    def test_inspect_apply_repeat_preserve_active_work_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            before = self.snapshot(fixture)
            inspected = self.tool(fixture, "inspect", "--isolated")
            self.assertEqual(inspected.returncode, 0, inspected.stdout + inspected.stderr)
            self.assertEqual(json.loads(inspected.stdout)["status"], "applicable")
            self.assertFalse(self.clone_path(fixture).exists())
            self.assertEqual(before, self.snapshot(fixture))
            applied = self.tool(fixture, "apply", "--isolated")
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertTrue(payload["isolated"])
            self.assertEqual(payload["status"], "applied-and-pushed")
            self.assertEqual(self.git(fixture["remote"], "rev-parse", "main^{tree}"), fixture["metadata"]["analytics_tree"])
            self.assertEqual(before, self.snapshot(fixture))
            repeated = self.tool(fixture, "apply", "--isolated")
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already-applied")
            self.assertEqual(json.loads(repeated.stdout)["result_commit"], payload["result_commit"])
            self.assertEqual(before, self.snapshot(fixture))
            self.assertEqual(self.git(self.clone_path(fixture), "rev-list", "--count", "main"), "2")
            hook = self.clone_path(fixture) / ".git/hooks/commit-msg"
            self.assertIn("commit_message_policy.py", hook.read_text())

    def test_default_mode_still_blocks_active_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            before = self.snapshot(fixture)
            result = self.tool(fixture, "apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("активной рабочей сессии", result.stdout)
            self.assertEqual(before, self.snapshot(fixture))

    def test_rejected_push_reuses_same_persistent_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            before = self.snapshot(fixture)
            hook = fixture["remote"] / "hooks/pre-receive"
            hook.write_text("#!/bin/sh\nexit 1\n")
            hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
            failed = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(failed.returncode, 0)
            first = self.receipt(fixture)
            self.assertEqual(first["status"], "committed-not-pushed")
            self.assertEqual(before, self.snapshot(fixture))
            hook.unlink()
            retried = self.tool(fixture, "apply", "--isolated")
            self.assertEqual(retried.returncode, 0, retried.stdout + retried.stderr)
            self.assertEqual(json.loads(retried.stdout)["result_commit"], first["result_commit"])
            self.assertEqual(self.git(self.clone_path(fixture), "rev-list", "--count", "main"), "2")
            self.assertEqual(before, self.snapshot(fixture))

    def test_whitespace_sha_tree_and_path_failures_never_change_remote_or_working_copy(self):
        for problem in ("whitespace", "sha", "tree", "paths"):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as temporary:
                fixture = self.active_fixture(Path(temporary), trailing_whitespace=problem == "whitespace")
                metadata = fixture["metadata"]
                if problem == "sha":
                    metadata["patch_sha256"] = "0" * 64
                elif problem == "tree":
                    metadata["analytics_tree"] = metadata["documents_tree"] = "a" * 40
                elif problem == "paths":
                    metadata["changed_paths"] = metadata["changed_paths"][:1]
                    metadata["changed_path_count"] = 1
                fixture["metadata_path"].write_text(json.dumps(metadata))
                before = self.snapshot(fixture)
                for command in ("inspect", "apply"):
                    result = self.tool(fixture, command, "--isolated")
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(before, self.snapshot(fixture))
                    self.assertEqual(self.git(fixture["remote"], "rev-parse", "main"), metadata["source_commit"])
                self.assertFalse((fixture["root"] / "reverse-patch-receipts").exists())

    def test_remote_advancement_is_not_hidden_by_old_local_main(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            (fixture["target"] / "README.md").write_text("Remote advances independently\n")
            self.git(fixture["target"], "add", "--", "README.md")
            self.git(fixture["target"], "commit", "-m", "Advance source")
            self.git(fixture["target"], "push", "origin", "main")
            remote = self.git(fixture["remote"], "rev-parse", "main")
            before = self.snapshot(fixture)
            inspected = self.tool(fixture, "inspect", "--isolated")
            self.assertEqual(inspected.returncode, 2, inspected.stdout + inspected.stderr)
            applied = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(applied.returncode, 0)
            self.assertIn("не совпадает с исходным коммитом", applied.stdout)
            self.assertEqual(before, self.snapshot(fixture))
            self.assertEqual(self.git(fixture["remote"], "rev-parse", "main"), remote)

    def test_dirty_unregistered_or_pending_work_is_not_bypassed(self):
        for problem in ("dirty", "unregistered", "pending"):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as temporary:
                fixture = self.active_fixture(Path(temporary))
                if problem == "dirty":
                    (fixture["repository"] / "README.md").write_text("unsaved\n")
                else:
                    path = fixture["root"] / ".workspace-state/collaboration.json"
                    data = json.loads(path.read_text())
                    if problem == "unregistered":
                        data["active_work"] = None
                    else:
                        data["active_work"]["status"] = "recovery-pending"
                    path.write_text(json.dumps(data))
                before = self.snapshot(fixture)
                result = self.tool(fixture, "apply", "--isolated")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(before, self.snapshot(fixture))

    def test_local_only_is_resumable_and_never_updates_working_refs(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            before = self.snapshot(fixture)
            local = self.tool(fixture, "apply", "--isolated", "--no-push")
            self.assertEqual(local.returncode, 0, local.stdout + local.stderr)
            commit = json.loads(local.stdout)["result_commit"]
            self.assertEqual(self.git(fixture["remote"], "rev-parse", "main"), fixture["metadata"]["source_commit"])
            pushed = self.tool(fixture, "apply", "--isolated")
            self.assertEqual(pushed.returncode, 0, pushed.stdout + pushed.stderr)
            self.assertEqual(json.loads(pushed.stdout)["result_commit"], commit)
            self.assertEqual(before, self.snapshot(fixture))

    def test_missing_or_foreign_clone_is_not_replaced_on_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            before = self.snapshot(fixture)
            clone = self.clone_path(fixture)
            clone.mkdir(parents=True)
            marker = clone / "keep.txt"
            marker.write_text("keep\n")
            result = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "keep\n")
            self.assertEqual(before, self.snapshot(fixture))

    def test_missing_clone_after_commit_cannot_create_a_replacement_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            result = self.tool(fixture, "apply", "--isolated", "--no-push")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            clone = self.clone_path(fixture)
            clone.rename(clone.with_name("retained-copy"))
            result = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("квитанция существует", result.stdout)
            self.assertFalse(clone.exists())

    def test_clone_with_alternate_object_storage_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            clone = self.clone_path(fixture)
            clone.parent.mkdir(parents=True)
            self.assertEqual(existing.run("git", "clone", "--shared", str(fixture["repository"]), str(clone)).returncode, 0)
            before = self.snapshot(fixture)
            result = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("общее хранилище", result.stdout)
            self.assertEqual(before, self.snapshot(fixture))

    def test_working_state_change_before_push_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            sys.path.insert(0, str(existing.ROOT / "scripts"))
            self.addCleanup(sys.path.remove, str(existing.ROOT / "scripts"))
            spec = importlib.util.spec_from_file_location("isolated_patch_test", existing.TOOL)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            args = module.parser().parse_args(["--root", str(fixture["root"]), "apply", "--isolated"])
            original_finalize = module.finalize_push
            state = fixture["root"] / ".workspace-state/active-mode.md"
            def change_before_push(*args, **kwargs):
                state.write_text("mode: execution-update\n")
                return original_finalize(*args, **kwargs)
            with patch.dict(os.environ, fixture["env"]), patch.object(module, "finalize_push", side_effect=change_before_push):
                with self.assertRaisesRegex(ValueError, "изменилась во время"):
                    module.apply_command(args)
            self.assertEqual(self.git(fixture["remote"], "rev-parse", "main"), fixture["metadata"]["source_commit"])
            self.assertEqual(self.receipt(fixture)["status"], "committed-not-pushed")
            self.assertEqual(state.read_text(), "mode: execution-update\n")

    def test_unrecorded_local_target_is_not_reported_as_pushed(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.active_fixture(Path(temporary))
            first = self.tool(fixture, "apply", "--isolated", "--no-push")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            receipt = fixture["root"] / "reverse-patch-receipts" / f"reverse-diff-{fixture['metadata']['artifact_id']}.receipt.json"
            receipt.unlink()
            before = self.snapshot(fixture)
            repeated = self.tool(fixture, "apply", "--isolated")
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("только локально", repeated.stdout)
            self.assertEqual(before, self.snapshot(fixture))
            self.assertEqual(self.git(fixture["remote"], "rev-parse", "main"), fixture["metadata"]["source_commit"])
