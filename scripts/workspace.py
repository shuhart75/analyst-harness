#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


CONFIG_NAME = ".analyst-workspace.json"
WORKSPACE_NAME = "analyst-workspace.code-workspace"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def harness_root(explicit: str | None = None) -> Path:
    return Path(explicit).expanduser().resolve() if explicit else Path(__file__).resolve().parents[1]


def checked_relative(root: Path, value: str, label: str) -> Path:
    candidate = (root / value).resolve()
    if candidate == root or root not in candidate.parents:
        raise ValueError(f"{label} должен быть относительным путём внутри рабочей области")
    return candidate


def load_config(root: Path) -> dict:
    path = root / CONFIG_NAME
    if not path.is_file():
        raise ValueError(
            "Первичная настройка не выполнена. LLM должна запросить способ подготовки "
            "аналитического и кодового репозиториев, затем выполнить workspace.py configure."
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Не удалось прочитать {path}: {exc}") from exc
    if payload.get("schema_version") != 1:
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
    if missing:
        with exclude.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write("\n# analyst-harness managed workspace\n")
            handle.write("\n".join(missing) + "\n")


def configure_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    validate_mode(args.analytical_mode, args.analytical_url, "аналитического репозитория")
    validate_mode(args.code_mode, args.code_url, "кодового репозитория")
    analytical = checked_relative(root, args.analytical_dir, "Путь аналитического репозитория")
    code = None if args.code_mode == "skip" else checked_relative(root, args.code_dir, "Путь кодового репозитория")
    if code == analytical:
        raise ValueError("Аналитический и кодовый репозитории должны находиться в разных каталогах")
    path = root / CONFIG_NAME
    if path.exists() and not args.force:
        raise ValueError(f"{path} уже существует; используй --force только для осознанной перенастройки")
    payload = {
        "schema_version": 1,
        "configured_at": utc_now(),
        "analytical": {
            "mode": args.analytical_mode,
            "path": os.path.relpath(analytical, root),
            "remote_url": args.analytical_url,
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


def git_root(path: Path) -> Path | None:
    result = run("git", "-C", str(path), "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def ensure_clone(path: Path, url: str, label: str) -> None:
    if not path.exists():
        result = run("git", "clone", url, str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось клонировать {label}: {result.stderr.strip()}")
    if git_root(path) != path:
        raise ValueError(f"{label} не является корнем Git-репозитория: {path}")
    remotes = run("git", "-C", str(path), "remote", "get-url", "--all", "origin")
    urls = {line.strip() for line in remotes.stdout.splitlines() if line.strip()}
    if url not in urls:
        raise ValueError(f"origin {label} не совпадает с сохранённым URL: {sorted(urls)}")


def ensure_created_analytical(root: Path, path: Path) -> None:
    if path.exists() and any(path.iterdir()) and git_root(path) != path:
        raise ValueError(f"Каталог для аналитического репозитория не пуст и не является Git-репозиторием: {path}")
    if not path.exists() or not any(path.iterdir()):
        result = run("bash", str(root / "scripts/scaffold-project.sh"), str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось создать аналитический проект: {(result.stdout + result.stderr).strip()}")
    elif not (path / ".workflow").is_dir():
        result = run("bash", str(root / "scripts/scaffold-project.sh"), str(path), "--merge")
        if result.returncode != 0:
            raise ValueError(f"Не удалось установить обвязку: {(result.stdout + result.stderr).strip()}")
    if git_root(path) != path:
        result = run("git", "init", "-b", "main", str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось создать Git-репозиторий: {result.stderr.strip()}")


def install_harness(root: Path, project: Path) -> None:
    result = run("bash", str(root / "scripts/scaffold-project.sh"), str(project), "--merge")
    if result.returncode != 0:
        raise ValueError(f"Не удалось установить обвязку в {project}: {(result.stdout + result.stderr).strip()}")


def ensure_created_code(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()) and git_root(path) != path:
        raise ValueError(f"Каталог кодового репозитория не пуст и не является Git-репозиторием: {path}")
    if git_root(path) != path:
        result = run("git", "init", "-b", "main", str(path))
        if result.returncode != 0:
            raise ValueError(f"Не удалось создать кодовый Git-репозиторий: {result.stderr.strip()}")


def detect_contours(code: Path) -> dict:
    result = {}
    for name in ("backend", "frontend"):
        if (code / name).is_dir():
            result[name] = {"path": name}
    return result or {"root": {"path": "."}}


def write_code_registry(project: Path, code_config: dict, code_path: Path | None) -> None:
    repositories = []
    default_repository = None
    if code_path:
        default_repository = "code"
        accepted = [code_config["remote_url"]] if code_config.get("remote_url") else []
        repositories.append({
            "id": "code",
            "purpose": "Кодовый репозиторий для проверки требований",
            "access": "read-only",
            "location": {
                "environment": "ANALYST_CODE_REPO",
                "relative_to_analytical": os.path.relpath(code_path, project),
            },
            "accepted_remote_urls": accepted,
            "expected_branch": None,
            "contours": detect_contours(code_path),
            "instruction_patterns": [
                "AGENTS.md", "**/AGENTS.md", "CLAUDE.md", "**/CLAUDE.md",
                "openspec/README.md", "**/openspec/README.md", ".sdd/README.md", "**/.sdd/README.md",
            ],
        })
    payload = {
        "schema_version": 2,
        "workspace": {
            "layout": "managed-by-analyst-harness",
            "code_optional": True,
            "default_repository": default_repository,
            "analytical_repository": {"id": "analytical", "accepted_remote_urls": []},
        },
        "repositories": repositories,
    }
    path = project / ".workflow/code-repos.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_workspace(root: Path, analytical: Path, code: Path | None) -> Path:
    folders = [{"name": "analytical", "path": os.path.relpath(analytical, root)}]
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
    config = load_config(root)
    analytical_config = config["analytical"]
    analytical = checked_relative(root, analytical_config["path"], "Путь аналитического репозитория")
    if analytical_config["mode"] == "clone":
        ensure_clone(analytical, analytical_config["remote_url"], "аналитический репозиторий")
        install_harness(root, analytical)
    else:
        ensure_created_analytical(root, analytical)

    code_config = config["code"]
    code = None
    if code_config["mode"] != "skip":
        code = checked_relative(root, code_config["path"], "Путь кодового репозитория")
        if code_config["mode"] == "clone":
            ensure_clone(code, code_config["remote_url"], "кодовый репозиторий")
        else:
            ensure_created_code(code)
    write_code_registry(analytical, code_config, code)
    workspace = write_workspace(root, analytical, code)
    print(json.dumps({
        "status": "ready",
        "analytical_repository": str(analytical),
        "code_repository": str(code) if code else None,
        "workspace": str(workspace),
    }, ensure_ascii=False, indent=2))
    return 0


def status_command(args: argparse.Namespace) -> int:
    root = harness_root(args.root)
    config = load_config(root)
    report = {"status": "ready", "config": str(root / CONFIG_NAME), "repositories": []}
    for key in ("analytical", "code"):
        item = config[key]
        if item["mode"] == "skip":
            report["repositories"].append({"kind": key, "mode": "skip", "path": None, "state": "disabled"})
            continue
        path = checked_relative(root, item["path"], f"Путь {key}")
        state = "ready" if git_root(path) == path else "missing"
        report["repositories"].append({"kind": key, "mode": item["mode"], "path": str(path), "state": state})
        if state != "ready":
            report["status"] = "incomplete"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ready" else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Первичная настройка рабочей области аналитика")
    result.add_argument("--root", help="Корень analyst-harness; обычно определяется автоматически")
    commands = result.add_subparsers(dest="command", required=True)

    configure = commands.add_parser("configure")
    configure.add_argument("--analytical-mode", required=True, choices=("clone", "create"))
    configure.add_argument("--analytical-url")
    configure.add_argument("--analytical-dir", default="analytical-project")
    configure.add_argument("--code-mode", required=True, choices=("clone", "create", "skip"))
    configure.add_argument("--code-url")
    configure.add_argument("--code-dir", default="code")
    configure.add_argument("--force", action="store_true")
    configure.set_defaults(handler=configure_command)

    bootstrap = commands.add_parser("bootstrap")
    bootstrap.set_defaults(handler=bootstrap_command)

    status = commands.add_parser("status")
    status.set_defaults(handler=status_command)
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
