#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import re
import sys


ROLE_COLORS = {
    "AN": "LightGreen",
    "BE": "LightBlue",
    "FE": "LightCoral",
    "QA": "Gold",
}


@dataclass
class StoryMap:
    story_id: str
    summary: str
    baseline_start: str
    baseline_duration: int
    state: str
    mapping_mode: str
    replaced_by: list[str]
    residual_virtual_tasks: list[str]
    depends_on: list[str]


@dataclass
class Task:
    task_id: str
    summary: str
    kind: str
    role: str
    estimate: int
    executor: str
    planned_start: str
    planned_finish: str
    actual_start: str
    actual_finish: str
    status: str
    progress: int
    related_stories: list[str]


def usage() -> None:
    print("Usage: sync-actual-progress-overlay.py <project-root> <quarter-id> [feature-slug ...]")


def clean_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def split_list(value: str) -> list[str]:
    value = clean_cell(value)
    if not value or value in {"-", "—"}:
        return []
    parts = re.split(r"\s*,\s*|\s*;\s*|<br\s*/?>", value)
    return [clean_cell(part) for part in parts if clean_cell(part)]


def to_alias(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value.upper()).strip("_")


def parse_date(value: str) -> date | None:
    value = clean_cell(value)
    if not value:
        return None
    match = re.fullmatch(r"(\d{4})[-/](\d{2})[-/](\d{2})", value)
    if not match:
        return None
    year, month, day = match.groups()
    return date(int(year), int(month), int(day))


def fmt_date(value: date) -> str:
    return f"{value:%Y/%m/%d}"


def parse_int(value: str, default: int = 0) -> int:
    match = re.search(r"\d+", clean_cell(value))
    return int(match.group(0)) if match else default


def load_closed_days(project_root: Path, quarter_id: str) -> set[date]:
    path = project_root / "planning" / quarter_id / "gantt/closed-days.txt"
    if not path.exists():
        return set()
    result: set[date] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parsed = parse_date(line)
        if parsed:
            result.add(parsed)
    return result


def is_open_day(value: date, closed_days: set[date]) -> bool:
    return value.weekday() < 5 and value not in closed_days


def next_open_day(value: date, closed_days: set[date]) -> date:
    current = value
    while not is_open_day(current, closed_days):
        current += timedelta(days=1)
    return current


def add_open_days(start: date, days: int, closed_days: set[date]) -> date:
    current = next_open_day(start, closed_days)
    if days <= 1:
        return current
    remaining = days - 1
    while remaining > 0:
        current += timedelta(days=1)
        if is_open_day(current, closed_days):
            remaining -= 1
    return current


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_tables(path: Path) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            i += 1
            continue
        headers = [clean_cell(cell) for cell in line.strip("|").split("|")]
        if i + 1 >= len(lines):
            break
        separator = [cell.strip() for cell in lines[i + 1].strip().strip("|").split("|")]
        if not is_separator_row(separator):
            i += 1
            continue
        i += 2
        rows: list[dict[str, str]] = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            cells = [clean_cell(cell) for cell in lines[i].strip().strip("|").split("|")]
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
            i += 1
        tables.append(rows)
    return tables


def first_table_with(path: Path, required_header: str) -> list[dict[str, str]]:
    for table in parse_tables(path):
        if table and required_header in table[0]:
            return table
    return []


def load_story_map(feature_dir: Path) -> list[StoryMap]:
    path = feature_dir / "planning/actualization.md"
    if not path.exists():
        return []
    rows = first_table_with(path, "Story ID")
    result: list[StoryMap] = []
    for row in rows:
        story_id = clean_cell(row.get("Story ID", ""))
        if not story_id:
            continue
        result.append(
            StoryMap(
                story_id=story_id,
                summary=clean_cell(row.get("Summary", story_id)),
                baseline_start=clean_cell(row.get("Baseline Start", "")),
                baseline_duration=parse_int(row.get("Baseline Duration (дн)", ""), 1),
                state=clean_cell(row.get("Actualization State", "virtual")).lower(),
                mapping_mode=clean_cell(row.get("Mapping Mode", "explicit")).lower(),
                replaced_by=split_list(row.get("Replaced By", "")),
                residual_virtual_tasks=split_list(row.get("Residual Virtual Tasks", "")),
                depends_on=split_list(row.get("Depends On", "")),
            )
        )
    return result


def progress_from_status(status: str) -> int:
    status = status.lower()
    if status in {"done", "closed", "complete", "completed"}:
        return 100
    if status in {"planned", "todo", "open", "backlog", "superseded"}:
        return 0
    if status in {"in_progress", "in progress", "doing"}:
        return 50
    return 0


def load_tasks(feature_dir: Path) -> dict[str, Task]:
    tasks: dict[str, Task] = {}
    for path in sorted(feature_dir.glob("slices/*/execution/tasks.md")):
        rows = first_table_with(path, "Jira")
        for row in rows:
            task_id = clean_cell(row.get("Jira", ""))
            if not task_id:
                continue
            status = clean_cell(row.get("Status", "planned"))
            progress_value = row.get("Progress %", "")
            progress = parse_int(progress_value, progress_from_status(status)) if progress_value else progress_from_status(status)
            tasks[task_id] = Task(
                task_id=task_id,
                summary=clean_cell(row.get("Summary", task_id)),
                kind=clean_cell(row.get("Kind", "virtual")).lower(),
                role=clean_cell(row.get("Role", "")),
                estimate=parse_int(row.get("Estimate (дн)", ""), 1),
                executor=clean_cell(row.get("Executor", "")),
                planned_start=clean_cell(row.get("Planned Start", "")),
                planned_finish=clean_cell(row.get("Planned Finish", "")),
                actual_start=clean_cell(row.get("Actual Start", "")),
                actual_finish=clean_cell(row.get("Actual Finish", "")),
                status=status,
                progress=progress,
                related_stories=split_list(row.get("Related Stories", "")),
            )
    return tasks


def task_start(task: Task) -> date | None:
    return parse_date(task.actual_start) or parse_date(task.planned_start)


def task_finish(task: Task) -> date | None:
    finish = parse_date(task.actual_finish) or parse_date(task.planned_finish)
    if finish:
        return finish
    start = task_start(task)
    if not start:
        return None
    return start + timedelta(days=max(task.estimate - 1, 0))


def role_color(role: str) -> str:
    return ROLE_COLORS.get(role.upper(), "Wheat")


def story_type(story: StoryMap, tasks: dict[str, Task]) -> str:
    summary = story.summary.lower()
    fe_keywords = [
        "страница",
        "список",
        "форма",
        "detail",
        "деталь",
        "детальная",
        "ui",
        "frontend",
        "workspace",
        "view",
    ]
    be_keywords = [
        "backend",
        "core",
        "жизненный цикл",
        "жц",
        "api",
        "бд",
        "integration",
        "интеграция",
        "model",
        "модель",
        "контракты",
        "logic",
        "логика",
    ]
    if any(keyword in summary for keyword in fe_keywords):
        return "FE"
    if any(keyword in summary for keyword in be_keywords):
        return "BE"

    counts: dict[str, int] = {}
    for task_id in mapped_task_ids(story, tasks):
        role = tasks[task_id].role.upper()
        if not role:
            continue
        counts[role] = counts.get(role, 0) + 1
    if counts:
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return ordered[0][0]
    return "GEN"


def render_task(task: Task) -> list[str]:
    alias = f"TASK_{to_alias(task.task_id)}"
    start = task_start(task)
    if not start:
        return [f"' Skip task without start date: {task.task_id}"]
    assignee = f" on {{{task.executor}}}" if task.executor else ""
    lines = [
        f"[{task.summary}] as [{alias}]{assignee} lasts {max(task.estimate, 1)} days",
        f"[{alias}] starts {fmt_date(start)}",
        f"[{alias}] is colored in {role_color(task.role)}",
        f"[{alias}] is {max(0, min(task.progress, 100))}% completed",
    ]
    return lines


def mapped_task_ids(story: StoryMap, tasks: dict[str, Task]) -> list[str]:
    ids = list(story.replaced_by)
    if story.state == "mixed":
        ids.extend(story.residual_virtual_tasks)
    if story.state == "virtual" and not ids:
        ids.extend(task_id for task_id, task in tasks.items() if story.story_id in task.related_stories)
    unique: list[str] = []
    for task_id in ids:
        if task_id not in unique and task_id in tasks and tasks[task_id].status.lower() != "superseded":
            unique.append(task_id)
    return unique


def story_progress(story: StoryMap, tasks: dict[str, Task]) -> int:
    task_ids = mapped_task_ids(story, tasks)
    if not task_ids:
        return 0
    total = 0
    weighted = 0
    for task_id in task_ids:
        task = tasks[task_id]
        estimate = max(task.estimate, 1)
        total += estimate
        weighted += estimate * max(0, min(task.progress, 100))
    return round(weighted / total) if total else 0


def story_dates(
    story: StoryMap,
    tasks: dict[str, Task],
    story_ends: dict[str, date],
    closed_days: set[date],
) -> tuple[date | None, date | None]:
    baseline_start = parse_date(story.baseline_start)
    baseline_finish = add_open_days(baseline_start, max(story.baseline_duration, 1), closed_days) if baseline_start else None
    task_ids = mapped_task_ids(story, tasks)
    starts = [task_start(tasks[task_id]) for task_id in task_ids]
    finishes = [task_finish(tasks[task_id]) for task_id in task_ids]
    starts = [item for item in starts if item]
    finishes = [item for item in finishes if item]

    if finishes:
        start_candidates = list(starts)
        if baseline_start:
            start_candidates.append(baseline_start)
        return min(start_candidates) if start_candidates else baseline_start, max(finishes)

    if story.depends_on:
        dep_finishes = [story_ends[dep] for dep in story.depends_on if dep in story_ends]
        if dep_finishes:
            start = next_open_day(max(dep_finishes) + timedelta(days=1), closed_days)
            return start, add_open_days(start, max(story.baseline_duration, 1), closed_days)

    return baseline_start, baseline_finish


def render_story(
    story: StoryMap,
    tasks: dict[str, Task],
    story_ends: dict[str, date],
    closed_days: set[date],
) -> tuple[list[str], date | None]:
    start, finish = story_dates(story, tasks, story_ends, closed_days)
    if not start:
        return [f"' Skip story without start date: {story.story_id}"], None
    alias = f"STORY_{to_alias(story.story_id)}"
    label = f"PLAN {story_type(story, tasks)} {story.summary}"
    progress = story_progress(story, tasks)
    color = "LightSteelBlue" if story.state == "virtual" else "Gainsboro"
    lines = [
        f"[{label}] as [{alias}] starts {fmt_date(start)}",
    ]
    if finish and finish >= start:
        lines.append(f"[{alias}] ends {fmt_date(finish)}")
    else:
        lines.append(f"[{alias}] lasts {max(story.baseline_duration, 1)} days")
    lines.extend(
        [
            f"[{alias}] is colored in {color}",
            f"[{alias}] is {progress}% completed",
        ]
    )
    return lines, finish


def render_feature(feature_dir: Path, feature_slug: str, closed_days: set[date]) -> str | None:
    stories = load_story_map(feature_dir)
    tasks = load_tasks(feature_dir)
    if not stories:
        return None

    lines = [
        f"' FEATURE: {feature_slug}",
        "' Actual-progress overlay:",
        "' - STORY rows are commander-plan stories actualized by linked execution tasks",
        "' - TASK rows are current execution tasks rendered once, with many-to-many links kept in markdown",
        "",
        "' Story layer",
    ]

    story_ends: dict[str, date] = {}
    for story in stories:
        rendered, finish = render_story(story, tasks, story_ends, closed_days)
        lines.append(f"' Story {story.story_id}: {story.state}, mapping={story.mapping_mode}")
        lines.extend(rendered)
        lines.append("")
        if finish:
            story_ends[story.story_id] = finish

    active_tasks = [task for task in tasks.values() if task.status.lower() != "superseded"]
    if active_tasks:
        lines.append("' Execution task layer")
        for task in sorted(active_tasks, key=lambda item: (task_start(item) or date.max, item.task_id)):
            lines.extend(render_task(task))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if len(sys.argv) < 3:
        usage()
        return 1

    project_root = Path(sys.argv[1])
    quarter_id = sys.argv[2]
    closed_days = load_closed_days(project_root, quarter_id)
    if len(sys.argv) > 3:
        feature_slugs = sys.argv[3:]
    else:
        feature_slugs = [path.name for path in sorted((project_root / "features").iterdir()) if path.is_dir()]

    target_dir = project_root / "planning" / quarter_id / "gantt/includes/actual-progress"
    target_dir.mkdir(parents=True, exist_ok=True)

    for feature_slug in feature_slugs:
        feature_dir = project_root / "features" / feature_slug
        if not feature_dir.exists():
            print(f"Skip missing feature: {feature_slug}")
            continue
        target = target_dir / f"FEATURE-{feature_slug}.puml"
        content = render_feature(feature_dir, feature_slug, closed_days)
        if content is None:
            if target.exists():
                target.unlink()
                print(f"Removed stale {target}")
            else:
                print(f"Skip feature without actualization map: {feature_slug}")
            continue
        target.write_text(content, encoding="utf-8")
        print(f"Wrote {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
