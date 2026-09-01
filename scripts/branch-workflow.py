#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from commit_message_policy import require_valid_commit_message


BRANCH = "main"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run("git", "-C", str(repository), *args)


def root_path(explicit: str | None) -> Path:
    return Path(explicit).expanduser().resolve() if explicit else Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Ожидался объект JSON: {path}")
    return value


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def workspace_state(root: Path) -> dict:
    return load_json(root / ".workspace-state/workspace.json")


def analytics_repository(root: Path) -> tuple[Path, str]:
    role = workspace_state(root).get("roles", {}).get("analytics", {})
    repository_id = role.get("repository")
    configured_path = role.get("path")
    if not repository_id or not configured_path:
        raise ValueError("Роль analytics не настроена")
    repository = Path(configured_path).resolve()
    top = git(repository, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != repository:
        raise ValueError(f"Роль analytics не является отдельным Git-репозиторием: {repository}")
    return repository, repository_id


def operation_lock(root: Path):
    path = root / ".workspace-state/branch-workflow.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("w", encoding="utf-8")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise ValueError("Другая операция уже изменяет рабочую область") from exc
    return handle


def head(repository: Path, revision: str = "HEAD") -> str:
    result = git(repository, "rev-parse", revision)
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(f"Не удалось определить коммит {revision}")
    return result.stdout.strip()


def current_branch(repository: Path) -> str:
    result = git(repository, "symbolic-ref", "--quiet", "--short", "HEAD")
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError("Репозиторий analytics находится вне именованной ветки")
    return result.stdout.strip()


def require_clean(repository: Path) -> None:
    status = git(repository, "status", "--porcelain=v1")
    if status.returncode != 0:
        raise ValueError(f"Не удалось проверить analytics: {status.stderr.strip()}")
    if status.stdout:
        raise ValueError("Репозиторий analytics содержит несохранённые изменения")


def is_ancestor(repository: Path, older: str, newer: str) -> bool:
    return git(repository, "merge-base", "--is-ancestor", older, newer).returncode == 0


def fetch_main(repository: Path) -> str:
    fetched = git(repository, "fetch", "origin", BRANCH)
    if fetched.returncode != 0:
        raise ValueError(f"Не удалось получить origin/{BRANCH}: {fetched.stderr.strip()}")
    return head(repository, f"origin/{BRANCH}")


def snapshot_id(operation: str, before: str, incoming: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = hashlib.sha256(f"{operation}:{before}:{incoming}".encode()).hexdigest()[:12]
    return f"{stamp}-{suffix}"


def snapshot_path(root: Path, identifier: str) -> Path:
    return root / ".workspace-state/analytics-snapshots" / identifier


def create_snapshot(
    root: Path,
    repository: Path,
    repository_id: str,
    operation: str,
    incoming: str,
) -> dict:
    before = head(repository)
    identifier = snapshot_id(operation, before, incoming)
    directory = snapshot_path(root, identifier)
    if directory.exists():
        metadata = load_json(directory / "snapshot.json")
        if metadata.get("before") != before or metadata.get("incoming") != incoming:
            raise ValueError(f"Идентификатор защитного снимка занят: {identifier}")
        return metadata
    metadata = {
        "schema_version": 1,
        "snapshot_id": identifier,
        "status": "prepared",
        "operation": operation,
        "repository": repository_id,
        "branch": current_branch(repository),
        "before": before,
        "incoming": incoming,
        "created_at": now(),
        "conflicts": [],
    }
    atomic_json(directory / "snapshot.json", metadata)
    prefix = f"refs/analyst-harness/analytics-snapshots/{identifier}"
    for side, commit in (("before", before), ("incoming", incoming)):
        updated = git(repository, "update-ref", f"{prefix}/{side}", commit)
        if updated.returncode != 0:
            raise ValueError(f"Не удалось закрепить {side} защитного снимка: {updated.stderr.strip()}")
    return metadata


def conflict_records(repository: Path) -> list[dict]:
    result = git(repository, "diff", "--name-only", "--diff-filter=U")
    if result.returncode != 0:
        raise ValueError(f"Не удалось определить конфликтующие пути: {result.stderr.strip()}")
    records: list[dict] = []
    for path in [line for line in result.stdout.splitlines() if line]:
        stages = git(repository, "ls-files", "-u", "--", path)
        if stages.returncode != 0:
            raise ValueError(f"Не удалось прочитать стороны конфликта {path}")
        blobs: dict[int, str] = {}
        for line in stages.stdout.splitlines():
            metadata, _, _ = line.partition("\t")
            fields = metadata.split()
            if len(fields) == 3:
                blobs[int(fields[2])] = fields[1]
        records.append({
            "path": path,
            "base_blob": blobs.get(1),
            "local_blob": blobs.get(2),
            "incoming_blob": blobs.get(3),
        })
    return records


def archive_conflicts(root: Path, repository: Path, snapshot: dict) -> dict:
    directory = snapshot_path(root, snapshot["snapshot_id"])
    archived = []
    for record in conflict_records(repository):
        key = hashlib.sha256(record["path"].encode("utf-8", errors="surrogateescape")).hexdigest()
        files: dict[str, str] = {}
        for side, field in (("base", "base_blob"), ("local", "local_blob"), ("incoming", "incoming_blob")):
            oid = record.get(field)
            if not oid:
                continue
            blob = subprocess.run(
                ("git", "-C", str(repository), "cat-file", "blob", oid),
                capture_output=True,
                check=False,
            )
            if blob.returncode != 0:
                raise ValueError(f"Не удалось сохранить сторону {side} конфликта {record['path']}")
            target = directory / "conflicts" / key / side
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob.stdout)
            files[side] = str(target)
        archived.append({**record, "archived_files": files})
    snapshot["status"] = "conflict"
    snapshot["conflicts"] = archived
    snapshot["updated_at"] = now()
    atomic_json(directory / "snapshot.json", snapshot)
    return snapshot


def finish_snapshot(root: Path, repository: Path, snapshot: dict, after: str) -> dict:
    snapshot["status"] = "completed"
    snapshot["after"] = after
    snapshot["after_tree"] = head(repository, f"{after}^{{tree}}")
    snapshot["updated_at"] = now()
    atomic_json(snapshot_path(root, snapshot["snapshot_id"]) / "snapshot.json", snapshot)
    prefix = f"refs/analyst-harness/analytics-snapshots/{snapshot['snapshot_id']}"
    updated = git(repository, "update-ref", f"{prefix}/after", after)
    if updated.returncode != 0:
        raise ValueError(f"Не удалось завершить защитный снимок: {updated.stderr.strip()}")
    return snapshot


def snapshot_summary(root: Path, snapshot: dict) -> dict:
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "status": snapshot["status"],
        "metadata": str(snapshot_path(root, snapshot["snapshot_id"]) / "snapshot.json"),
        "conflicting_paths": [item["path"] for item in snapshot.get("conflicts", [])],
    }


def update_feature_command(args: argparse.Namespace) -> int:
    root = root_path(args.root)
    repository, repository_id = analytics_repository(root)
    branch = current_branch(repository)
    if not branch.startswith("feature/"):
        raise ValueError("Обновление разрешено только для ветки feature/<feature>/<analyst>")
    require_clean(repository)
    incoming = fetch_main(repository)
    before = head(repository)
    if is_ancestor(repository, incoming, before):
        print(json.dumps({
            "status": "current",
            "branch": branch,
            "before": before,
            "incoming": incoming,
            "after": before,
            "protective_snapshot": None,
        }, ensure_ascii=False, indent=2))
        return 0
    operation = "feature-main-fast-forward" if is_ancestor(repository, before, incoming) else "feature-main-merge"
    snapshot = create_snapshot(root, repository, repository_id, operation, incoming)
    if operation.endswith("fast-forward"):
        merged = git(repository, "merge", "--ff-only", f"origin/{BRANCH}")
    else:
        merge_message = f"Merge origin/{BRANCH} into {branch}"
        require_valid_commit_message(merge_message)
        merged = git(
            repository,
            "-c", "user.name=Analyst Harness",
            "-c", "user.email=analyst-harness@local.invalid",
            "merge", "--no-ff", f"origin/{BRANCH}",
            "-m", merge_message,
        )
    if merged.returncode != 0:
        snapshot = archive_conflicts(root, repository, snapshot)
        aborted = git(repository, "merge", "--abort")
        if aborted.returncode != 0:
            raise ValueError(
                f"Конфликт сохранён в снимке {snapshot['snapshot_id']}, но слияние не удалось отменить: "
                f"{aborted.stderr.strip()}"
            )
        raise ValueError(json.dumps({
            "status": "blocked",
            "reason": "feature-main-merge-conflict",
            "branch": branch,
            "conflicting_paths": [item["path"] for item in snapshot["conflicts"]],
            "protective_snapshot": snapshot_summary(root, snapshot),
            "allowed_next_action": "запросить у аналитика решение по одному пути",
            "forbidden_actions": ["git add -A", "git add .", "git reset", "git rebase", "force push"],
        }, ensure_ascii=False))
    after = head(repository)
    snapshot = finish_snapshot(root, repository, snapshot, after)
    require_clean(repository)
    print(json.dumps({
        "status": "fast-forwarded" if operation.endswith("fast-forward") else "merged",
        "branch": branch,
        "before": before,
        "incoming": incoming,
        "after": after,
        "protective_snapshot": snapshot_summary(root, snapshot),
    }, ensure_ascii=False, indent=2))
    return 0


def fast_forward_main_command(args: argparse.Namespace) -> int:
    root = root_path(args.root)
    repository, repository_id = analytics_repository(root)
    if current_branch(repository) != BRANCH:
        raise ValueError("Быстрое обновление разрешено только для main")
    require_clean(repository)
    incoming = fetch_main(repository)
    before = head(repository)
    if before == incoming:
        print(json.dumps({
            "status": "current",
            "before": before,
            "incoming": incoming,
            "after": before,
            "protective_snapshot": None,
        }, ensure_ascii=False, indent=2))
        return 0
    if not is_ancestor(repository, before, incoming):
        raise ValueError(
            "Локальная main не является предком origin/main; сохрани отдельную линию "
            "в рабочей ветке через миграцию"
        )
    snapshot = create_snapshot(root, repository, repository_id, "analytics-main-fast-forward", incoming)
    merged = git(repository, "merge", "--ff-only", f"origin/{BRANCH}")
    if merged.returncode != 0:
        raise ValueError(f"Быстрое обновление main завершилось ошибкой: {merged.stderr.strip()}")
    snapshot = finish_snapshot(root, repository, snapshot, incoming)
    print(json.dumps({
        "status": "fast-forwarded",
        "before": before,
        "incoming": incoming,
        "after": incoming,
        "protective_snapshot": snapshot_summary(root, snapshot),
    }, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Защищённое обновление веток аналитического репозитория")
    result.add_argument("--root", help="Корень analyst-harness")
    commands = result.add_subparsers(dest="command", required=True)
    update = commands.add_parser("update-feature")
    update.set_defaults(handler=update_feature_command)
    fast_forward = commands.add_parser("fast-forward-main")
    fast_forward.set_defaults(handler=fast_forward_main_command)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        handle = operation_lock(root_path(args.root))
        try:
            return args.handler(args)
        finally:
            handle.close()
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
