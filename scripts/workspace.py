#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from workspace_paths import ensure_local_state, state_root
from workspace_entrypoint import embedded_harness_paths, write_local_entrypoint
from commit_message_policy import HOOK_MARKER


CONFIG_NAME = ".analyst-workspace.json"
WORKSPACE_NAME = "analyst-workspace.code-workspace"
PROJECT_PATHS = ("baseline", "context", "features", "planning", "releases")
CODE_PUSH_DISABLED = "DISABLED_BY_ANALYST_HARNESS"


def install_commit_message_hook(repository: Path, policy_script: Path) -> Path:
    configured = run("git", "-C", str(repository), "config", "--get", "core.hooksPath")
    hook_result = run(
        "git", "-C", str(repository), "rev-parse", "--path-format=absolute",
        "--git-path", "hooks/commit-msg",
    )
    if hook_result.returncode != 0 or not hook_result.stdout.strip():
        raise ValueError("Не удалось определить путь Git hook commit-msg")
    hook = Path(hook_result.stdout.strip()).resolve()
    existing = hook.read_text(encoding="utf-8") if hook.is_file() else ""
    if configured.returncode == 0 and configured.stdout.strip() and HOOK_MARKER not in existing:
        raise ValueError(
            "Настроен несовместимый core.hooksPath; bootstrap остановлен, потому что "
            "запрет идентификаторов трекеров в сообщениях коммитов нельзя гарантировать"
        )
    if existing and HOOK_MARKER not in existing:
        raise ValueError(
            "Обнаружен сторонний commit-msg hook; bootstrap не будет его перезаписывать "
            "и не продолжит работу без обязательной защиты сообщений коммитов"
        )
    hook.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "#!/bin/sh\n"
        f"# {HOOK_MARKER}\n"
        f"exec python3 {shlex.quote(str(policy_script.resolve()))} \"$1\"\n"
    )
    temporary = hook.with_name(f".{hook.name}.analyst-harness.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.chmod(temporary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    temporary.replace(hook)
    return hook


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def harness_root(explicit: str | None = None) -> Path:
    return Path(explicit).expanduser().resolve() if explicit else Path(__file__).resolve().parents[1]


def checked_path(root: Path, value: str, label: str) -> Path:
    candidate = (root / value).resolve()
    if candidate == root or root not in candidate.parents:
        raise ValueError(f"{label} должен быть относительным путём внутри рабочей области")
    return candidate


def git_root(path: Path) -> Path | None:
    result = run("git", "-C", str(path), "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def misplaced_project_paths(root: Path) -> list[str]:
    return [name for name in PROJECT_PATHS if (root / name).exists()]


def require_clean_harness_boundary(root: Path) -> None:
    misplaced = misplaced_project_paths(root)
    if misplaced:
        raise ValueError(
            "Проектные каталоги ошибочно созданы в корне обвязки: "
            + ", ".join(misplaced)
            + ". Перенеси их в репозиторий роли analytics до продолжения"
        )


def load_config(root: Path) -> dict:
    path = root / CONFIG_NAME
    if not path.is_file():
        raise ValueError(
            "Первичная настройка не выполнена. LLM должна последовательно запросить способ "
            "подготовки аналитического и кодового репозиториев, затем выполнить configure."
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать {path}: {exc}") from exc
    if payload.get("schema_version") != 2:
        raise ValueError(f"Неподдерживаемая схема {path}")
    return payload


def validate_mode(mode: str, url: str | None, label: str) -> None:
    if mode == "clone" and not url:
        raise ValueError(f"Для клонирования {label} требуется URL")
    if mode != "clone" and url:
        raise ValueError(f"URL для {label} допустим только в режиме clone")


def register_local_excludes(root: Path, paths: list[Path]) -> None:
    git_path = run("git", "-C", str(root), "rev-parse", "--git-path", "info/exclude")
    if git_path.returncode != 0:
        return
    exclude = Path(git_path.stdout.strip())
    if not exclude.is_absolute():
        exclude = root / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    entries = ["/" + os.path.relpath(path, root).rstrip("/") + "/" for path in paths]
    missing = [entry for entry in entries if entry not in existing.splitlines()]
    if not missing:
        return
    with exclude.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n"):
            handle.write("\n")
        handle.write("\n# analyst-harness workspace repositories\n")
        handle.write("\n".join(missing) + "\n")


def configure_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    validate_mode(args.analytical_mode, args.analytical_url, "аналитического репозитория")
    validate_mode(args.code_mode, args.code_url, "кодового репозитория")
    analytical = checked_path(root, args.analytical_dir, "Путь аналитического репозитория")
    code = None if args.code_mode == "skip" else checked_path(root, args.code_dir, "Путь кодового репозитория")
    if analytical == code:
        raise ValueError("Аналитический и кодовый репозитории должны находиться в разных каталогах")
    path = root / CONFIG_NAME
    if path.exists() and not args.force:
        raise ValueError(f"{path} уже существует; --force допустим только для осознанной перенастройки")
    payload = {
        "schema_version": 2,
        "configured_at": utc_now(),
        "analytical": {
            "mode": args.analytical_mode,
            "path": os.path.relpath(analytical, root),
            "remote_url": args.analytical_url,
            "scaffold_mode": "none" if args.preserve_analytical_tree else "merge",
        },
        "code": {
            "mode": args.code_mode,
            "path": os.path.relpath(code, root) if code else None,
            "remote_url": args.code_url,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    register_local_excludes(root, [analytical] + ([code] if code else []))
    print(json.dumps({"status": "configured", "config": str(path), **payload}, ensure_ascii=False, indent=2))
    return 0


def ensure_clone(path: Path, url: str, label: str) -> None:
    if not path.exists():
        result = run("git", "clone", url, str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось клонировать {label}: {result.stderr.strip()}")
    if git_root(path) != path:
        raise ValueError(f"{label} не является корнем Git-репозитория: {path}")
    remotes = run("git", "-C", str(path), "remote", "get-url", "--all", "origin")
    current = {line.strip() for line in remotes.stdout.splitlines() if line.strip()}
    if url not in current:
        raise ValueError(f"origin {label} не совпадает с сохранённым URL: {sorted(current)}")


def disable_code_push(path: Path) -> None:
    result = run("git", "-C", str(path), "config", "remote.origin.pushurl", CODE_PUSH_DISABLED)
    if result.returncode != 0:
        raise ValueError(f"Не удалось запретить отправку в кодовый репозиторий: {result.stderr.strip()}")


def require_code_push_disabled(path: Path) -> None:
    result = run("git", "-C", str(path), "remote", "get-url", "--push", "origin")
    if result.returncode != 0 or result.stdout.strip() != CODE_PUSH_DISABLED:
        raise ValueError(
            "Для существующего кодового репозитория не закреплён запрет отправки; "
            "аналитическая обвязка не будет менять его настройки"
        )


def ensure_content_only(path: Path) -> None:
    embedded = embedded_harness_paths(path)
    if embedded:
        raise ValueError(
            "Аналитический репозиторий содержит встроенную обвязку: "
            + ", ".join(embedded)
            + ". Сначала перенеси проектные данные во внешнюю структуру; автоматическое удаление запрещено."
        )


def ensure_analytical(root: Path, source: Path, config: dict) -> Path:
    path = checked_path(root, config["path"], "Путь аналитического репозитория")
    if config["mode"] == "clone":
        ensure_clone(path, config["remote_url"], "аналитический репозиторий")
        ensure_content_only(path)
        scaffold_mode = config.get("scaffold_mode", "merge")
        if scaffold_mode == "merge":
            result = run("bash", str(source / "scripts/scaffold-project.sh"), str(path), "--merge")
            if result.returncode != 0:
                raise ValueError(
                    f"Не удалось дополнить структуру проекта: {(result.stdout + result.stderr).strip()}"
                )
        elif scaffold_mode != "none":
            raise ValueError(f"Неподдерживаемый analytical.scaffold_mode: {scaffold_mode}")
        return path
    if path.exists() and any(path.iterdir()) and git_root(path) != path:
        raise ValueError(f"Каталог аналитического репозитория не пуст: {path}")
    if not path.exists() or not any(path.iterdir()):
        result = run("bash", str(source / "scripts/scaffold-project.sh"), str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось создать аналитический проект: {(result.stdout + result.stderr).strip()}")
    ensure_content_only(path)
    if git_root(path) != path:
        result = run("git", "init", "-b", "main", str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось создать Git-репозиторий: {result.stderr.strip()}")
    return path


def ensure_code(root: Path, config: dict) -> Path | None:
    if config["mode"] == "skip":
        return None
    path = checked_path(root, config["path"], "Путь кодового репозитория")
    if config["mode"] == "clone":
        created = not path.exists()
        ensure_clone(path, config["remote_url"], "кодовый репозиторий")
        if created:
            disable_code_push(path)
        else:
            require_code_push_disabled(path)
    else:
        path.mkdir(parents=True, exist_ok=True)
        if any(path.iterdir()) and git_root(path) != path:
            raise ValueError(f"Каталог кодового репозитория не пуст: {path}")
        if git_root(path) != path:
            result = run("git", "init", "-b", "main", str(path))
            if result.returncode != 0:
                raise ValueError(f"Не удалось создать кодовый Git-репозиторий: {result.stderr.strip()}")
    return path


def detect_contours(code: Path) -> dict:
    contours = {name: {"path": name} for name in ("backend", "frontend") if (code / name).is_dir()}
    return contours or {"root": {"path": "."}}


def write_code_registry(analytical: Path, analytical_config: dict, code: Path | None, code_config: dict) -> Path:
    repositories = []
    if code:
        repositories.append({
            "id": "code",
            "purpose": "Кодовый репозиторий для проверки требований",
            "access": "read-only",
            "write_policy": {
                "mode": "operations-only",
                "allowed_paths": ["requirements-exchange/**"],
                "allowed_operations": [
                    "initial-clone-or-create",
                    "git-pull-ff-only-via-workspace",
                    "requirements-exchange-publish-via-isolated-clone",
                ],
                "user_prompt_can_override": False,
            },
            "location": {
                "environment": "ANALYST_CODE_REPO",
                "relative_to_analytical": os.path.relpath(code, analytical),
            },
            "accepted_remote_urls": [code_config["remote_url"]] if code_config.get("remote_url") else [],
            "expected_branch": None,
            "contours": detect_contours(code),
            "instruction_patterns": [
                "AGENTS.md", "**/AGENTS.md", "CLAUDE.md", "**/CLAUDE.md",
                "openspec/README.md", "**/openspec/README.md", ".sdd/README.md", "**/.sdd/README.md",
            ],
        })
    payload = {
        "schema_version": 3,
        "workspace": {
            "layout": "sibling-clones",
            "code_optional": True,
            "analytical_repository": {
                "id": "analytical",
                "accepted_remote_urls": [analytical_config["remote_url"]] if analytical_config.get("remote_url") else [],
            },
        },
        "repositories": repositories,
    }
    path = state_root() / "code-repos.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_workspace(root: Path, analytical: Path, code: Path | None) -> Path:
    folders = [
        {"name": "analyst-harness", "path": "."},
        {"name": "analytical", "path": os.path.relpath(analytical, root)},
    ]
    if code:
        folders.append({"name": "code-read-only", "path": os.path.relpath(code, root)})
    payload = {
        "folders": folders,
        "settings": {
            "files.exclude": {"**/.git": True},
            "search.exclude": {"**/.git": True, "**/node_modules": True, "**/build": True},
        },
    }
    path = root / WORKSPACE_NAME
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def bootstrap_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    require_clean_harness_boundary(root)
    source = Path(__file__).resolve().parents[1]
    config = load_config(root)
    ensure_local_state()
    analytical = ensure_analytical(root, source, config["analytical"])
    commit_message_hooks = []
    if git_root(root) == root:
        commit_message_hooks.append(
            install_commit_message_hook(root, source / "scripts/commit_message_policy.py")
        )
    commit_message_hooks.append(
        install_commit_message_hook(analytical, source / "scripts/commit_message_policy.py")
    )
    code = ensure_code(root, config["code"])
    entrypoint = write_local_entrypoint(analytical, root, code)
    registry = write_code_registry(analytical, config["analytical"], code, config["code"])
    workspace = write_workspace(root, analytical, code)
    workspace_state = state_root() / "workspace.json"
    workspace_state.write_text(json.dumps({
        "schema_version": 1,
        "prepared_at": utc_now(),
        "roles": {
            "analytics": {
                "repository": analytical.name,
                "path": str(analytical),
                "access": "read-write",
            },
            "code": {
                "path": str(code) if code else None,
                "access": "read-only" if code else "disabled",
                "allowed_paths": ["requirements-exchange/**"] if code else [],
                "allowed_operations": (
                    [
                        "initial-clone-or-create",
                        "git-pull-ff-only-via-workspace",
                        "requirements-exchange-publish-via-isolated-clone",
                    ] if code else []
                ),
            },
        },
        "project_root": str(analytical),
        "local_entrypoint": str(entrypoint),
        "commit_message_hooks": [str(path) for path in commit_message_hooks],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "ready",
        "roles": {
            "analytics": str(analytical),
            "code": str(code) if code else None,
        },
        "analytical_repository": str(analytical),
        "code_repository": str(code) if code else None,
        "code_registry": str(registry),
        "commit_message_hooks": [str(path) for path in commit_message_hooks],
        "workspace": str(workspace),
    }, ensure_ascii=False, indent=2))
    return 0


def status_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    config = load_config(root)
    misplaced = misplaced_project_paths(root)
    analytical = checked_path(root, config["analytical"]["path"], "Путь analytics")
    report = {
        "status": "invalid" if misplaced else "ready",
        "config": str(root / CONFIG_NAME),
        "project_root": str(analytical),
        "misplaced_project_paths": misplaced,
        "repositories": [],
    }
    for key in ("analytical", "code"):
        item = config[key]
        if item["mode"] == "skip":
            report["repositories"].append({"kind": key, "mode": "skip", "state": "disabled"})
            continue
        path = checked_path(root, item["path"], f"Путь {key}")
        state = "ready" if git_root(path) == path else "missing"
        if state != "ready":
            report["status"] = "incomplete"
        report["repositories"].append({"kind": key, "mode": item["mode"], "path": str(path), "state": state})
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ready" else 1


def update_code_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    config = load_config(root)
    code_config = config["code"]
    if code_config["mode"] != "clone":
        raise ValueError("Защищённый git pull доступен только для клонированного кодового репозитория")
    code = checked_path(root, code_config["path"], "Путь кодового репозитория")
    if git_root(code) != code:
        raise ValueError("Кодовый репозиторий не развёрнут; сначала выполни bootstrap")
    ensure_clone(code, code_config["remote_url"], "кодовый репозиторий")
    require_code_push_disabled(code)
    dirty = run("git", "-C", str(code), "status", "--porcelain=v1")
    if dirty.returncode != 0 or dirty.stdout:
        raise ValueError("Кодовый репозиторий содержит локальные изменения; git pull запрещён")
    branch = run("git", "-C", str(code), "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch.returncode != 0:
        raise ValueError("Кодовый репозиторий находится в detached HEAD; git pull запрещён")
    name = branch.stdout.strip()
    before = run("git", "-C", str(code), "rev-parse", "HEAD").stdout.strip()
    pulled = run(
        "git", "-C", str(code), "-c", "core.hooksPath=/dev/null",
        "pull", "--ff-only", "--no-rebase", "origin", name,
    )
    if pulled.returncode != 0:
        raise ValueError(f"Не удалось выполнить защищённый git pull кодового репозитория: {pulled.stderr.strip()}")
    after_status = run("git", "-C", str(code), "status", "--porcelain=v1")
    if after_status.returncode != 0 or after_status.stdout:
        raise ValueError("Защищённый git pull оставил изменённое рабочее дерево; требуется владелец кода")
    require_code_push_disabled(code)
    after = run("git", "-C", str(code), "rev-parse", "HEAD").stdout.strip()
    print(json.dumps({
        "status": "updated" if before != after else "current",
        "role": "code",
        "branch": name,
        "before": before,
        "after": after,
        "operation": "git-pull-ff-only-via-workspace",
    }, ensure_ascii=False, indent=2))
    return 0


def project_root_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    require_clean_harness_boundary(root)
    config = load_config(root)
    project = checked_path(root, config["analytical"]["path"], "Путь роли analytics")
    if git_root(project) != project:
        raise ValueError("Репозиторий роли analytics не развёрнут; сначала выполни bootstrap")
    print(project)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Настраиваемая рабочая область аналитика")
    result.add_argument("--root", help="Корень analyst-harness; обычно определяется автоматически")
    commands = result.add_subparsers(dest="command", required=True)
    configure = commands.add_parser("configure")
    configure.add_argument("--analytical-mode", choices=("clone", "create"), required=True)
    configure.add_argument("--analytical-url")
    configure.add_argument("--analytical-dir", default="analytical-project")
    configure.add_argument(
        "--preserve-analytical-tree",
        action="store_true",
        help="Подключить клонированный analytics без добавления scaffold-файлов",
    )
    configure.add_argument("--code-mode", choices=("clone", "create", "skip"), required=True)
    configure.add_argument("--code-url")
    configure.add_argument("--code-dir", default="code")
    configure.add_argument("--force", action="store_true")
    configure.set_defaults(handler=configure_command)
    bootstrap = commands.add_parser("bootstrap")
    bootstrap.set_defaults(handler=bootstrap_command)
    project_root_parser = commands.add_parser("project-root")
    project_root_parser.set_defaults(handler=project_root_command)
    status = commands.add_parser("status")
    status.set_defaults(handler=status_command)
    update_code = commands.add_parser("update-code")
    update_code.set_defaults(handler=update_code_command)
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
