#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


CONFIG_NAME = ".analyst-workspace.json"
DEFAULT_BRANCH = "main"
ARTIFACT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
OID_PATTERN = re.compile(r"^[0-9a-f]{40,64}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def git(repository: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return run("git", "-C", str(repository), *args, env=env)


def root_path(explicit: str | None) -> Path:
    return Path(explicit).expanduser().resolve() if explicit else Path(__file__).resolve().parents[1]


def state_root(root: Path) -> Path:
    override = os.environ.get("ANALYST_HARNESS_STATE_ROOT", "").strip()
    return Path(override).expanduser().resolve() if override else root / ".workspace-state"


@contextmanager
def operation_lock(root: Path):
    path = state_root(root) / "reverse-patch-apply.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("w", encoding="utf-8")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise ValueError("Другая операция уже изменяет аналитический репозиторий") from exc
    try:
        yield
    finally:
        handle.close()


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Корень JSON должен быть объектом: {path}")
    return payload


def project_repository(root: Path) -> Path:
    config = load_json(root / CONFIG_NAME)
    if config.get("schema_version") != 2:
        raise ValueError("Неподдерживаемая схема настройки analyst-harness")
    relative = config.get("analytical", {}).get("path")
    if not isinstance(relative, str) or not relative:
        raise ValueError("В настройке отсутствует путь роли analytics")
    repository = (root / relative).resolve()
    if repository == root or root not in repository.parents:
        raise ValueError("Путь роли analytics выходит за границы рабочей области")
    top = git(repository, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != repository:
        raise ValueError(f"Роль analytics не является отдельным Git-репозиторием: {repository}")
    return repository


def exact_path(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Путь в квитанции должен быть строкой")
    parsed = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or "\x00" in value
        or "\n" in value
        or "\r" in value
        or parsed.is_absolute()
        or any(part in {"", ".", ".."} for part in parsed.parts)
        or parsed.as_posix() != value
    ):
        raise ValueError(f"Недопустимый путь в квитанции: {value!r}")
    return value


def require_oid(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not OID_PATTERN.fullmatch(value):
        raise ValueError(f"Некорректное поле {key} в квитанции")
    return value


def patch_candidates(metadata_path: Path, payload: dict) -> list[Path]:
    artifact_id = str(payload["artifact_id"])
    names = [f"reverse-diff-{artifact_id}.patch"]
    if metadata_path.name == "reverse-diff-latest.json":
        names.append("reverse-diff-latest.patch")
    for key in ("patch", "latest_patch"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            names.append(Path(value).name)
    result = []
    for name in names:
        candidate = metadata_path.parent / name
        if candidate.is_file() and candidate not in result:
            result.append(candidate)
    return result


def validate_metadata(metadata_path: Path) -> tuple[dict, Path | None]:
    payload = load_json(metadata_path)
    if payload.get("schema_version") != 2:
        raise ValueError("Поддерживается только схема 2 обратной заплаты")
    artifact_id = payload.get("artifact_id")
    if not isinstance(artifact_id, str) or not ARTIFACT_PATTERN.fullmatch(artifact_id):
        raise ValueError("Некорректный artifact_id")
    if payload.get("status") == "unavailable":
        raise ValueError("Квитанция сообщает, что обратная заплата недоступна")
    for key in ("verified", "tree_verified", "content_policy_verified"):
        if payload.get(key) is not True:
            raise ValueError(f"Обратная заплата не прошла обязательную проверку {key}")
    if "diff_check_verified" in payload and payload["diff_check_verified"] is not True:
        raise ValueError("Обратная заплата не прошла проверку пробельного оформления")
    source_commit = require_oid(payload, "source_commit")
    analytics_commit = require_oid(payload, "analytics_commit")
    source_tree = require_oid(payload, "source_tree")
    analytics_tree = require_oid(payload, "analytics_tree")
    if payload.get("documents_commit") not in {None, analytics_commit}:
        raise ValueError("analytics_commit и documents_commit не совпадают")
    if payload.get("documents_tree") not in {None, analytics_tree}:
        raise ValueError("analytics_tree и documents_tree не совпадают")
    source_branch = payload.get("source_branch", DEFAULT_BRANCH)
    if source_branch != DEFAULT_BRANCH:
        raise ValueError(f"Неподдерживаемая исходная ветка: {source_branch}")
    analytics_branch = payload.get("analytics_branch", DEFAULT_BRANCH)
    if analytics_branch != DEFAULT_BRANCH:
        raise ValueError(f"Неподдерживаемая целевая ветка: {analytics_branch}")
    included_features = payload.get("included_features", [])
    if not isinstance(included_features, list) or any(
        not isinstance(item, str) or not item for item in included_features
    ):
        raise ValueError("included_features должен быть списком непустых строк")
    included_commits = payload.get("included_analytics_commits", [])
    if not isinstance(included_commits, list):
        raise ValueError("included_analytics_commits должен быть списком")
    for item in included_commits:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("commit"), str)
            or not OID_PATTERN.fullmatch(item["commit"])
            or not isinstance(item.get("subject"), str)
        ):
            raise ValueError("included_analytics_commits содержит некорректную запись")
    changed = payload.get("changed_paths")
    if not isinstance(changed, list):
        raise ValueError("changed_paths должен быть списком")
    changed_paths = [exact_path(item) for item in changed]
    if len(changed_paths) != len(set(changed_paths)):
        raise ValueError("changed_paths содержит повторяющиеся пути")
    if payload.get("changed_path_count") != len(changed_paths):
        raise ValueError("changed_path_count не совпадает с changed_paths")
    identical = payload.get("repositories_identical") is True
    patch_sha256 = payload.get("patch_sha256")
    if identical:
        if source_tree != analytics_tree or patch_sha256 is not None or changed_paths:
            raise ValueError("Некорректная квитанция совпадающих деревьев")
        return payload, None
    if source_tree == analytics_tree:
        raise ValueError("Для разных состояний указаны одинаковые деревья")
    if not changed_paths:
        raise ValueError("Для разных деревьев changed_paths не может быть пустым")
    if not isinstance(patch_sha256, str) or not SHA256_PATTERN.fullmatch(patch_sha256):
        raise ValueError("Некорректная контрольная сумма patch_sha256")
    matching = [
        candidate
        for candidate in patch_candidates(metadata_path, payload)
        if hashlib.sha256(candidate.read_bytes()).hexdigest() == patch_sha256
    ]
    if not matching:
        raise ValueError("Рядом с квитанцией не найдена заплата с указанной контрольной суммой")
    return payload, matching[0]


def search_directories(root: Path, extra: list[str]) -> list[Path]:
    directories = [root / "reverse-patch-inbox", Path.home() / "Downloads"]
    directories.extend(Path(item).expanduser().resolve() for item in extra)
    result = []
    for directory in directories:
        if directory not in result:
            result.append(directory)
    return result


def discover(root: Path, extra: list[str]) -> tuple[list[dict], list[dict]]:
    by_artifact: dict[str, dict] = {}
    signatures: dict[str, tuple[str, str, str | None]] = {}
    conflicts: set[str] = set()
    invalid = []
    for directory in search_directories(root, extra):
        if not directory.is_dir():
            continue
        for metadata_path in sorted(directory.rglob("reverse-diff-*.json")):
            if metadata_path.name.endswith(".receipt.json"):
                continue
            try:
                payload, patch = validate_metadata(metadata_path)
                artifact_id = str(payload["artifact_id"])
                signature = (
                    payload["source_commit"],
                    payload["analytics_commit"],
                    payload.get("patch_sha256"),
                )
                if artifact_id in conflicts:
                    continue
                if artifact_id in signatures and signatures[artifact_id] != signature:
                    by_artifact.pop(artifact_id, None)
                    conflicts.add(artifact_id)
                    invalid.append({
                        "status": "invalid",
                        "artifact_id": artifact_id,
                        "metadata": str(metadata_path),
                        "error": "Один artifact_id относится к разным обратным заплатам",
                    })
                    continue
                record = {
                    "status": "valid",
                    "artifact_id": artifact_id,
                    "created_at": payload.get("created_at"),
                    "metadata": str(metadata_path),
                    "patch": str(patch) if patch else None,
                    "source_commit": payload["source_commit"],
                    "analytics_commit": payload["analytics_commit"],
                    "changed_path_count": payload["changed_path_count"],
                    "included_features": payload.get("included_features", []),
                }
                existing = by_artifact.get(artifact_id)
                if existing is None or metadata_path.name != "reverse-diff-latest.json":
                    by_artifact[artifact_id] = record
                    signatures[artifact_id] = signature
            except ValueError as exc:
                invalid.append({"status": "invalid", "metadata": str(metadata_path), "error": str(exc)})
    return sorted(by_artifact.values(), key=lambda item: item["artifact_id"]), invalid


def resolve_input(root: Path, args: argparse.Namespace) -> tuple[Path, dict, Path | None]:
    if args.metadata:
        metadata_path = Path(args.metadata).expanduser().resolve()
    else:
        valid, _ = discover(root, args.directory)
        if args.artifact_id:
            matches = [item for item in valid if item["artifact_id"] == args.artifact_id]
        else:
            matches = valid
        if not matches:
            raise ValueError("Подходящая проверенная обратная заплата не найдена")
        if len(matches) != 1:
            identifiers = ", ".join(item["artifact_id"] for item in matches)
            raise ValueError(f"Найдено несколько обратных заплат; укажи artifact_id: {identifiers}")
        metadata_path = Path(matches[0]["metadata"])
    payload, patch = validate_metadata(metadata_path)
    if args.artifact_id and payload["artifact_id"] != args.artifact_id:
        raise ValueError("Указанный artifact_id не совпадает с квитанцией")
    return metadata_path, payload, patch


def require_clean(repository: Path) -> None:
    status = git(repository, "status", "--porcelain=v1", "-z")
    if status.returncode != 0:
        raise ValueError(f"Не удалось проверить рабочее дерево: {status.stderr.strip()}")
    if status.stdout:
        raise ValueError("Аналитический репозиторий содержит локальные изменения; применение запрещено")
    if git(repository, "rev-parse", "--verify", "MERGE_HEAD").returncode == 0:
        raise ValueError("В аналитическом репозитории выполняется незавершённое слияние")


def current_branch(repository: Path) -> str:
    result = git(repository, "symbolic-ref", "--quiet", "--short", "HEAD")
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError("Аналитический репозиторий находится вне именованной ветки")
    return result.stdout.strip()


def revision(repository: Path, value: str) -> str:
    result = git(repository, "rev-parse", value)
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(f"Не удалось определить {value}")
    return result.stdout.strip()


def is_ancestor(repository: Path, older: str, newer: str) -> bool:
    return git(repository, "merge-base", "--is-ancestor", older, newer).returncode == 0


def receipt_path(root: Path, artifact_id: str) -> Path:
    return root / "reverse-patch-receipts" / f"reverse-diff-{artifact_id}.receipt.json"


def write_receipt(root: Path, payload: dict) -> Path:
    path = receipt_path(root, str(payload["artifact_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def remote_head(repository: Path, branch: str) -> str | None:
    result = git(repository, "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
    if result.returncode != 0:
        raise ValueError(f"Не удалось проверить origin/{branch}: {result.stderr.strip()}")
    line = result.stdout.strip()
    return line.split()[0] if line else None


def base_receipt(metadata_path: Path, patch: Path | None, metadata: dict, repository: Path) -> dict:
    remote = git(repository, "remote", "get-url", "origin")
    if remote.returncode != 0 or not remote.stdout.strip():
        raise ValueError("Для аналитического репозитория не настроен origin")
    return {
        "schema_version": 1,
        "artifact_type": "reverse-diff-application-receipt",
        "artifact_id": metadata["artifact_id"],
        "source_repository": metadata.get("source_repository"),
        "source_remote": remote.stdout.strip(),
        "source_branch": metadata.get("source_branch", DEFAULT_BRANCH),
        "expected_source_commit": metadata["source_commit"],
        "expected_source_tree": metadata["source_tree"],
        "analytics_repository": metadata.get("analytics_repository"),
        "analytics_commit": metadata["analytics_commit"],
        "analytics_tree": metadata["analytics_tree"],
        "patch_sha256": metadata.get("patch_sha256"),
        "changed_paths": metadata["changed_paths"],
        "included_features": metadata.get("included_features", []),
        "included_analytics_commits": metadata.get("included_analytics_commits", []),
        "metadata_file": str(metadata_path),
        "patch_file": str(patch) if patch else None,
        "repository": str(repository),
    }


def verify_patch_tree(repository: Path, patch: Path, expected_tree: str) -> None:
    git_objects = git(repository, "rev-parse", "--git-path", "objects")
    if git_objects.returncode != 0 or not git_objects.stdout.strip():
        raise ValueError(f"Не удалось определить хранилище объектов Git: {git_objects.stderr.strip()}")
    original_objects = Path(git_objects.stdout.strip())
    if not original_objects.is_absolute():
        original_objects = (repository / original_objects).resolve()
    with tempfile.TemporaryDirectory(prefix="analyst-reverse-patch-") as raw_temporary:
        temporary = Path(raw_temporary)
        index = temporary / "index"
        objects = temporary / "objects"
        objects.mkdir()
        alternates = [str(original_objects)]
        inherited_alternates = os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES", "").strip()
        if inherited_alternates:
            alternates.append(inherited_alternates)
        environment = {
            **os.environ,
            "GIT_INDEX_FILE": str(index),
            "GIT_OBJECT_DIRECTORY": str(objects),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": os.pathsep.join(alternates),
        }
        read = git(repository, "read-tree", "HEAD", env=environment)
        if read.returncode != 0:
            raise ValueError(f"Не удалось подготовить временный индекс: {read.stderr.strip()}")
        checked = git(
            repository,
            "apply", "--cached", "--check", "--binary", "--whitespace=error-all",
            str(patch),
            env=environment,
        )
        if checked.returncode != 0:
            detail = checked.stdout.strip() or checked.stderr.strip()
            raise ValueError(
                "Заплата не прошла предварительную проверку применимости "
                f"и пробельного оформления: {detail}"
            )
        applied = git(
            repository,
            "apply", "--cached", "--binary", "--whitespace=error-all",
            str(patch),
            env=environment,
        )
        if applied.returncode != 0:
            detail = applied.stdout.strip() or applied.stderr.strip()
            raise ValueError(f"Заплата не применима к временному индексу: {detail}")
        tree = git(repository, "write-tree", env=environment)
        if tree.returncode != 0 or tree.stdout.strip() != expected_tree:
            raise ValueError("Применение заплаты не воспроизводит целевое дерево analytics")


def rollback_patch(repository: Path, patch: Path) -> None:
    reverted = git(repository, "apply", "--reverse", "--index", "--binary", str(patch))
    if reverted.returncode != 0:
        raise ValueError(
            "Не удалось отменить применённую, но не зафиксированную заплату: "
            f"{reverted.stderr.strip()}"
        )
    require_clean(repository)


def finalize_push(root: Path, repository: Path, receipt: dict, no_push: bool) -> dict:
    branch = str(receipt["source_branch"])
    result_commit = str(receipt["result_commit"])
    if no_push:
        receipt.update({"status": "applied-locally", "pushed": False, "remote_commit": remote_head(repository, branch)})
        path = write_receipt(root, receipt)
        return {**receipt, "receipt": str(path)}
    pushed = git(repository, "push", "origin", f"HEAD:{branch}")
    if pushed.returncode != 0:
        receipt.update({
            "status": "committed-not-pushed",
            "pushed": False,
            "push_error": pushed.stderr.strip(),
            "updated_at": utc_now(),
        })
        path = write_receipt(root, receipt)
        raise ValueError(
            f"Коммит {result_commit} создан, но отправка не выполнена. "
            f"Квитанция сохранена в {path}: {pushed.stderr.strip()}"
        )
    published = remote_head(repository, branch)
    if published != result_commit:
        raise ValueError(f"После отправки origin/{branch} не указывает на созданный коммит {result_commit}")
    receipt.update({
        "status": "applied-and-pushed",
        "pushed": True,
        "remote_commit": published,
        "pushed_at": utc_now(),
        "updated_at": utc_now(),
    })
    path = write_receipt(root, receipt)
    return {**receipt, "receipt": str(path)}


def existing_receipt_result(
    root: Path,
    repository: Path,
    metadata: dict,
    no_push: bool,
) -> dict | None:
    path = receipt_path(root, str(metadata["artifact_id"]))
    if not path.is_file():
        return None
    receipt = load_json(path)
    for key, expected in (
        ("artifact_id", metadata["artifact_id"]),
        ("analytics_tree", metadata["analytics_tree"]),
        ("patch_sha256", metadata.get("patch_sha256")),
    ):
        if receipt.get(key) != expected:
            raise ValueError(f"Существующая квитанция применения не совпадает по полю {key}")
    result_commit = receipt.get("result_commit")
    if not isinstance(result_commit, str) or not OID_PATTERN.fullmatch(result_commit):
        return None
    if git(repository, "cat-file", "-e", f"{result_commit}^{{commit}}").returncode != 0:
        raise ValueError("Коммит из существующей квитанции отсутствует в репозитории")
    if revision(repository, f"{result_commit}^{{tree}}") != metadata["analytics_tree"]:
        raise ValueError("Коммит из существующей квитанции не воспроизводит целевое дерево")
    origin_commit = revision(repository, f"origin/{receipt['source_branch']}")
    if is_ancestor(repository, result_commit, origin_commit):
        receipt.update({
            "status": "applied-and-pushed",
            "pushed": True,
            "remote_commit": origin_commit,
            "updated_at": utc_now(),
        })
        receipt_file = write_receipt(root, receipt)
        return {**receipt, "status": "already-applied", "receipt": str(receipt_file)}
    if revision(repository, "HEAD") != result_commit:
        raise ValueError("После местного применения появились другие коммиты; автоматическая отправка запрещена")
    return finalize_push(root, repository, receipt, no_push)


def discover_command(args: argparse.Namespace) -> int:
    root = root_path(args.root)
    valid, invalid = discover(root, args.directory)
    print(json.dumps({
        "status": "candidates-found" if valid else "no-valid-candidates",
        "valid": valid,
        "invalid": invalid,
        "next_action": (
            "применить единственный artifact_id"
            if len(valid) == 1
            else "выбрать один artifact_id" if valid else "передать проверенную пару json + patch"
        ),
    }, ensure_ascii=False, indent=2))
    return 0 if valid else 2


def inspect_command(args: argparse.Namespace) -> int:
    root = root_path(args.root)
    metadata_path, metadata, patch = resolve_input(root, args)
    repository = project_repository(root)
    branch = current_branch(repository)
    head = revision(repository, "HEAD")
    tree = revision(repository, "HEAD^{tree}")
    status = git(repository, "status", "--porcelain=v1")
    applicable = (
        branch == metadata.get("source_branch", DEFAULT_BRANCH)
        and not status.stdout
        and head == metadata["source_commit"]
        and tree == metadata["source_tree"]
    )
    validation_error = None
    if applicable and patch is not None:
        try:
            verify_patch_tree(repository, patch, metadata["analytics_tree"])
        except ValueError as exc:
            applicable = False
            validation_error = str(exc)
    print(json.dumps({
        "status": "applicable" if applicable else "not-applicable",
        "reason": "patch-validation-failed" if validation_error else None,
        "validation_error": validation_error,
        "artifact_id": metadata["artifact_id"],
        "metadata": str(metadata_path),
        "patch": str(patch) if patch else None,
        "repository": str(repository),
        "branch": branch,
        "head": head,
        "tree": tree,
        "clean": not bool(status.stdout),
        "expected_branch": metadata.get("source_branch", DEFAULT_BRANCH),
        "expected_source_commit": metadata["source_commit"],
        "expected_source_tree": metadata["source_tree"],
        "target_tree": metadata["analytics_tree"],
        "included_features": metadata.get("included_features", []),
    }, ensure_ascii=False, indent=2))
    return 0 if applicable else 2


def require_collaboration_ready_for_apply(root: Path) -> None:
    local_state = state_root(root)
    workspace_path = local_state / "workspace.json"
    if not workspace_path.is_file():
        return
    collaboration_path = local_state / "collaboration.json"
    if not collaboration_path.is_file():
        raise ValueError(
            "Совместная работа ещё не настроена; обратную заплату нельзя применять до одноразовой миграции"
        )
    collaboration = load_json(collaboration_path)
    if (
        collaboration.get("schema_version") != 1
        or collaboration.get("mode") != "multi-user-branches"
    ):
        raise ValueError(f"Повреждена настройка совместной работы: {collaboration_path}")
    active = collaboration.get("active_work")
    if active:
        branch = active.get("branch") if isinstance(active, dict) else "unknown"
        raise ValueError(
            f"Обратную заплату нельзя применять при активной рабочей сессии {branch}; "
            "сначала заверши или разреши её"
        )


def apply_command(args: argparse.Namespace) -> int:
    root = root_path(args.root)
    require_collaboration_ready_for_apply(root)
    with operation_lock(root):
        metadata_path, metadata, patch = resolve_input(root, args)
        repository = project_repository(root)
        require_clean(repository)
        branch = current_branch(repository)
        expected_branch = metadata.get("source_branch", DEFAULT_BRANCH)
        if branch != expected_branch:
            raise ValueError(f"Ожидалась ветка {expected_branch}, выбрана {branch}")
        if git(repository, "remote", "get-url", "origin").returncode != 0:
            raise ValueError("Для аналитического репозитория не настроен origin")
        pulled = git(
            repository,
            "-c", "core.hooksPath=/dev/null",
            "pull", "--ff-only", "--no-rebase", "origin", branch,
        )
        if pulled.returncode != 0:
            raise ValueError(f"Не удалось безопасно обновить {branch}: {pulled.stderr.strip()}")
        require_clean(repository)
        existing = existing_receipt_result(root, repository, metadata, args.no_push)
        if existing is not None:
            print(json.dumps(existing, ensure_ascii=False, indent=2))
            return 0
        head = revision(repository, "HEAD")
        tree = revision(repository, "HEAD^{tree}")
        if tree == metadata["analytics_tree"]:
            receipt = base_receipt(metadata_path, patch, metadata, repository)
            receipt.update({
                "status": "observed-already-integrated",
                "result_commit": head,
                "result_tree": tree,
                "pushed": True,
                "remote_commit": revision(repository, f"origin/{branch}"),
                "observed_at": utc_now(),
            })
            path = write_receipt(root, receipt)
            print(json.dumps({**receipt, "receipt": str(path)}, ensure_ascii=False, indent=2))
            return 0
        if head != metadata["source_commit"] or tree != metadata["source_tree"]:
            raise ValueError(
                "Текущая source/main не совпадает с исходным коммитом и деревом квитанции. "
                "Заплату применять нельзя; требуется заново синхронизировать documents и сформировать новую."
            )
        if patch is None:
            raise ValueError("Квитанция не содержит заплату, но текущее дерево не совпадает с целевым")
        verify_patch_tree(repository, patch, metadata["analytics_tree"])
        for variable in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
            identity = git(repository, "var", variable)
            if identity.returncode != 0:
                raise ValueError(f"Не настроена Git-идентификация {variable}: {identity.stderr.strip()}")
        checked = git(
            repository,
            "apply", "--index", "--check", "--binary", "--whitespace=error-all",
            str(patch),
        )
        if checked.returncode != 0:
            raise ValueError(f"Заплата не применима к рабочему дереву: {checked.stderr.strip()}")
        applied = git(
            repository,
            "apply", "--index", "--binary", "--whitespace=error-all", str(patch),
        )
        if applied.returncode != 0:
            raise ValueError(f"Не удалось применить заплату: {applied.stderr.strip()}")
        staged = git(repository, "diff", "--cached", "--name-only", "-z", "HEAD", "--", ".")
        try:
            staged_paths = [item for item in staged.stdout.split("\0") if item]
            if staged.returncode != 0 or sorted(staged_paths) != sorted(metadata["changed_paths"]):
                raise ValueError("Состав применённых путей не совпадает с квитанцией")
            tree_after_apply = git(repository, "write-tree")
            if tree_after_apply.returncode != 0 or tree_after_apply.stdout.strip() != metadata["analytics_tree"]:
                raise ValueError("Индекс после применения не совпадает с целевым деревом analytics")
            whitespace = git(repository, "diff", "--cached", "--check")
            if whitespace.returncode != 0:
                detail = whitespace.stdout.strip() or whitespace.stderr.strip()
                raise ValueError(f"Проверка применённых изменений завершилась ошибкой: {detail}")
            features = ", ".join(metadata.get("included_features", [])) or "нет"
            committed = git(
                repository,
                "-c", "core.hooksPath=/dev/null",
                "commit",
                "-m", f"sync: применить обратную заплату {metadata['artifact_id']}",
                "-m", (
                    f"Analytics-Commit: {metadata['analytics_commit']}\n"
                    f"Analytics-Tree: {metadata['analytics_tree']}\n"
                    f"Included-Features: {features}"
                ),
            )
            if committed.returncode != 0:
                raise ValueError(f"Не удалось создать интеграционный коммит: {committed.stderr.strip()}")
        except (OSError, ValueError):
            if revision(repository, "HEAD") == head:
                rollback_patch(repository, patch)
            raise
        result_commit = revision(repository, "HEAD")
        result_tree = revision(repository, "HEAD^{tree}")
        if result_tree != metadata["analytics_tree"]:
            raise ValueError("Созданный коммит не совпадает с целевым деревом analytics")
        require_clean(repository)
        receipt = base_receipt(metadata_path, patch, metadata, repository)
        receipt.update({
            "status": "committed-not-pushed",
            "result_commit": result_commit,
            "result_tree": result_tree,
            "committed_at": utc_now(),
            "pushed": False,
        })
        write_receipt(root, receipt)
        result = finalize_push(root, repository, receipt, args.no_push)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0


def add_input_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--metadata", help="Путь к reverse-diff-*.json")
    command.add_argument("--artifact-id", help="Идентификатор найденной заплаты")
    command.add_argument("--directory", action="append", default=[], help="Дополнительный каталог поиска")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Безопасный приём обратной заплаты в рабочий source")
    result.add_argument("--root", help="Корень analyst-harness; обычно определяется автоматически")
    commands = result.add_subparsers(dest="command", required=True)
    discover_parser = commands.add_parser("discover")
    discover_parser.add_argument("--directory", action="append", default=[], help="Дополнительный каталог поиска")
    discover_parser.set_defaults(handler=discover_command)
    inspect_parser = commands.add_parser("inspect")
    add_input_arguments(inspect_parser)
    inspect_parser.set_defaults(handler=inspect_command)
    apply_parser = commands.add_parser("apply")
    add_input_arguments(apply_parser)
    apply_parser.add_argument("--no-push", action="store_true", help="Создать коммит, но не отправлять его")
    apply_parser.set_defaults(handler=apply_command)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        return args.handler(args)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
