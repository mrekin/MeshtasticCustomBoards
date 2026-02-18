#!/usr/bin/env python3
"""Generate a GitHub Actions build matrix from build_list YAML files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-list", default="build_list.yaml", help="Path to build list YAML")
    parser.add_argument(
        "--mode",
        default="release",
        choices=("daily", "release", "all"),
        help="Filter by build_options.<mode>_build",
    )
    parser.add_argument(
        "--devices",
        default="",
        help="Comma-separated filters: build_name, pio_target, or device_name",
    )
    parser.add_argument(
        "--source-repo",
        default="",
        help="Override firmware source repo (<owner>/<repo>)",
    )
    parser.add_argument(
        "--source-ref",
        default="",
        help="Firmware ref (branch/tag/sha). Empty means default branch",
    )
    parser.add_argument(
        "--version-label",
        default="",
        help="Override artifact version label",
    )
    parser.add_argument(
        "--parallel-jobs",
        default="4",
        help="Maximum parallel matrix jobs",
    )
    parser.add_argument(
        "--github-output",
        default="",
        help="Path to GITHUB_OUTPUT file for workflow outputs",
    )
    return parser.parse_args()


def parse_build_options(raw: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(raw, dict):
        result.update(raw)
        return result
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                result.update(item)
    return result


def include_variant(mode: str, options: dict[str, Any]) -> bool:
    if mode == "all":
        return True
    if mode == "daily":
        return bool(options.get("daily_build"))
    if mode == "release":
        return bool(options.get("release_build"))
    return False


def parse_device_filter(raw: str) -> set[str]:
    if not raw.strip():
        return set()
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def sanitize_label(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw.strip())
    cleaned = cleaned.strip("-")
    return cleaned or "snapshot"


def detect_source_repo(config: dict[str, Any], override: str) -> str:
    if override.strip():
        return override.strip()
    source = str(config.get("github_source", "")).strip()
    if not source:
        raise ValueError("build_list YAML does not define 'github_source'")
    return source


def detect_version_label(mode: str, source_ref: str, override: str) -> str:
    if override.strip():
        return sanitize_label(override)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    if mode == "daily":
        return f"daily-{stamp}"
    if source_ref.strip():
        return sanitize_label(source_ref)
    return f"snapshot-{stamp}"


def build_matrix(
    config: dict[str, Any],
    mode: str,
    device_filters: set[str],
) -> list[dict[str, str]]:
    variants = config.get("build_variants", [])
    if not isinstance(variants, list):
        raise ValueError("build_list YAML has invalid 'build_variants' section")

    matrix: list[dict[str, str]] = []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        options = parse_build_options(variant.get("build_options"))
        if not include_variant(mode, options):
            continue

        pio_target = str(variant.get("pio_target", "")).strip()
        if not pio_target:
            continue

        build_name = str(variant.get("build_name") or pio_target).strip()
        device_name = str(variant.get("device_name") or build_name).strip()
        device_type = str(variant.get("device_type") or "").strip()
        build_flags = str(variant.get("build_flags") or "").strip()
        pio_build_target = str(variant.get("pio_build_target") or "").strip()
        user_specs = str(variant.get("user_specs") or "").strip()

        if device_filters:
            tokens = {build_name.lower(), pio_target.lower(), device_name.lower()}
            if tokens.isdisjoint(device_filters):
                continue

        matrix.append(
            {
                "device_type": device_type,
                "device_name": device_name,
                "build_name": build_name,
                "pio_target": pio_target,
                "build_flags": build_flags,
                "pio_build_target": pio_build_target,
                "user_specs": user_specs,
            }
        )
    return matrix


def parse_parallel_jobs(raw: str) -> str:
    try:
        jobs = int(raw)
    except ValueError as exc:
        raise ValueError(f"parallel_jobs must be integer, got: {raw}") from exc
    if jobs < 1:
        raise ValueError("parallel_jobs must be >= 1")
    return str(jobs)


def write_github_output(path: Path, outputs: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        for key, value in outputs.items():
            fh.write(f"{key}={value}\n")


def main() -> int:
    args = parse_args()
    build_list_path = Path(args.build_list)
    if not build_list_path.exists():
        raise FileNotFoundError(f"build list not found: {build_list_path}")

    with build_list_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    device_filters = parse_device_filter(args.devices)
    matrix_entries = build_matrix(config, args.mode, device_filters)
    source_repo = detect_source_repo(config, args.source_repo)
    source_ref = args.source_ref.strip()
    version_label = detect_version_label(args.mode, source_ref, args.version_label)
    parallel_jobs = parse_parallel_jobs(args.parallel_jobs)

    matrix_obj = {"include": matrix_entries}
    outputs = {
        "matrix": json.dumps(matrix_obj, separators=(",", ":"), ensure_ascii=True),
        "source_repo": source_repo,
        "source_ref": source_ref,
        "version_label": version_label,
        "parallel_jobs": parallel_jobs,
        "devices_count": str(len(matrix_entries)),
    }

    if args.github_output:
        write_github_output(Path(args.github_output), outputs)

    print(
        json.dumps(
            {
                "build_list": str(build_list_path),
                "mode": args.mode,
                "source_repo": source_repo,
                "source_ref": source_ref,
                "version_label": version_label,
                "parallel_jobs": parallel_jobs,
                "devices_count": len(matrix_entries),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    if not matrix_entries:
        print("warning: matrix is empty after filtering", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
