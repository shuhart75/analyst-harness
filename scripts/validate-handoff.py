#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REQ_RE = re.compile(r"\bREQ-[A-Z0-9-]+\b")
SCN_RE = re.compile(r"\bSCN-[A-Z0-9-]+\b")

PACKAGE_STATUSES = {
    "pending",
    "no-change-required",
    "proposal-created",
    "proposal-created-with-blocked-items",
    "blocked",
    "rejected-package",
}
COVERAGE_STATUSES = {
    "pending",
    "implemented-as-required",
    "implemented-with-deviation",
    "partially-implemented",
    "not-implemented",
    "blocked-product-decision",
    "blocked-dependency",
    "not-applicable",
}
ACTIONS = {
    "pending",
    "no-change",
    "include-in-proposal",
    "return-product-question",
    "wait-for-dependency",
    "not-applicable",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_ids(entries: Any, key: str, expected: list[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(entries, list):
        return [f"{label} must be an array"]
    actual = [entry.get(key) for entry in entries if isinstance(entry, dict)]
    if len(actual) != len(entries) or any(not isinstance(value, str) for value in actual):
        errors.append(f"{label} contains an invalid {key}")
    if len(actual) != len(set(actual)):
        errors.append(f"{label} contains duplicate ids")
    if set(actual) != set(expected):
        errors.append(f"{label} does not exactly match manifest ids")
    return errors


def validate(package: Path, receipt_name: str) -> list[str]:
    errors: list[str] = []
    manifest_path = package / "manifest.json"
    request_path = package / "request.md"
    receipt_path = package / receipt_name

    manifest = load_json(manifest_path)
    receipt = load_json(receipt_path)

    if manifest.get("schema_version") != 5:
        errors.append("manifest schema_version must be 5")
    policy = manifest.get("reconciliation_policy", {})
    if policy.get("mode") != "per-item-continuation":
        errors.append("reconciliation_policy.mode must be per-item-continuation")
    if set(manifest.get("allowed_package_statuses", [])) != PACKAGE_STATUSES:
        errors.append("manifest package statuses do not match the canonical protocol")
    if set(manifest.get("allowed_coverage_statuses", [])) != COVERAGE_STATUSES:
        errors.append("manifest coverage statuses do not match the canonical protocol")
    if set(manifest.get("allowed_actions", [])) != ACTIONS:
        errors.append("manifest actions do not match the canonical protocol")

    payload_paths: set[str] = set()
    for item in manifest.get("payload", []):
        if not isinstance(item, dict):
            errors.append("manifest payload entry must be an object")
            continue
        relative = item.get("path")
        expected_hash = item.get("sha256")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"invalid payload path: {relative!r}")
            continue
        if relative in payload_paths:
            errors.append(f"duplicate payload path: {relative}")
            continue
        payload_paths.add(relative)
        payload_file = package / relative
        if not payload_file.is_file():
            errors.append(f"missing payload file: {relative}")
        elif sha256(payload_file) != expected_hash:
            errors.append(f"payload checksum mismatch: {relative}")

    request_text = request_path.read_text(encoding="utf-8")
    manifest_requirements = manifest.get("requirements", [])
    manifest_scenarios = manifest.get("scenarios", [])
    if set(REQ_RE.findall(request_text)) != set(manifest_requirements):
        errors.append("request requirement ids do not match manifest")
    if set(SCN_RE.findall(request_text)) != set(manifest_scenarios):
        errors.append("request scenario ids do not match manifest")

    if receipt.get("schema_version") != 3:
        errors.append("receipt schema_version must be 3")
    for key in ("package_id", "package_revision"):
        if receipt.get(key) != manifest.get(key):
            errors.append(f"receipt {key} does not match manifest")
    if receipt.get("request_id") != manifest.get("request", {}).get("id"):
        errors.append("receipt request_id does not match manifest")
    if receipt.get("request_version") != manifest.get("request", {}).get("version"):
        errors.append("receipt request_version does not match manifest")
    if receipt.get("request_sha256") != sha256(request_path):
        errors.append("receipt request_sha256 does not match request.md")
    if set(receipt.get("allowed_statuses", [])) != PACKAGE_STATUSES:
        errors.append("receipt package statuses do not match the canonical protocol")
    if set(receipt.get("allowed_coverage_statuses", [])) != COVERAGE_STATUSES:
        errors.append("receipt coverage statuses do not match the canonical protocol")
    if set(receipt.get("allowed_actions", [])) != ACTIONS:
        errors.append("receipt actions do not match the canonical protocol")

    errors.extend(exact_ids(receipt.get("requirement_coverage"), "requirement", manifest_requirements, "requirement_coverage"))
    errors.extend(exact_ids(receipt.get("scenario_coverage"), "scenario", manifest_scenarios, "scenario_coverage"))

    for label in ("requirement_coverage", "scenario_coverage"):
        for entry in receipt.get(label, []):
            if not isinstance(entry, dict):
                continue
            if entry.get("status") not in COVERAGE_STATUSES:
                errors.append(f"invalid coverage status in {label}: {entry.get('status')}")
            if entry.get("action") not in ACTIONS:
                errors.append(f"invalid action in {label}: {entry.get('action')}")

    for key in ("remaining_delta", "baseline_feedback", "requirements_feedback"):
        if not isinstance(receipt.get(key), list):
            errors.append(f"receipt {key} must be an array")

    if receipt.get("status") not in PACKAGE_STATUSES:
        errors.append(f"invalid receipt status: {receipt.get('status')}")
    if receipt.get("status") == "no-change-required" and receipt.get("remaining_delta"):
        errors.append("no-change-required receipt must have empty remaining_delta")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an analyst-to-SDD handoff package")
    parser.add_argument("package", type=Path)
    parser.add_argument("--receipt", default="receipt.template.json")
    args = parser.parse_args()

    try:
        errors = validate(args.package.resolve(), args.receipt)
    except (OSError, ValueError) as exc:
        print(f"Handoff validation failed: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Handoff package OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
