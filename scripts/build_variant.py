#!/usr/bin/env python3
"""Build one firmware variant and collect artifacts for GitHub Actions."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

import yaml

ARTIFACT_SUFFIXES = (".bin", ".hex", ".zip", ".uf2", ".mt.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, help="Firmware source directory")
    parser.add_argument("--device-type", required=True, help="Device type (esp32/nrf52/rp2040)")
    parser.add_argument("--device-name", required=True, help="Human readable device name")
    parser.add_argument("--build-name", required=True, help="Build identifier")
    parser.add_argument("--pio-target", required=True, help="PlatformIO environment")
    parser.add_argument("--build-flags", default="", help="Extra PLATFORMIO_BUILD_FLAGS")
    parser.add_argument("--pio-build-target", default="", help="Extra PlatformIO target")
    parser.add_argument(
        "--user-specs-file",
        default="",
        help="Path to user specs YAML (optional)",
    )
    parser.add_argument("--version-label", required=True, help="Version folder name")
    parser.add_argument("--output-dir", required=True, help="Artifacts output directory")
    parser.add_argument("--build-notes", default="", help="Optional text for ver.info")
    parser.add_argument(
        "--build-date",
        default="",
        help="Build date string. If empty, current UTC date is used",
    )
    return parser.parse_args()


def run_command(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print("+", " ".join(shlex.quote(token) for token in command))
    subprocess.run(command, cwd=str(cwd), env=env, check=True)


def is_number_like(raw: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", raw))


def stringify_spec(key: str, value: object) -> str:
    if isinstance(value, bool):
        return f"-D{key}={'true' if value else 'false'}"
    if isinstance(value, (int, float)):
        return f"-D{key}={value}"

    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
    else:
        text = str(value)

    if text.startswith("{") or text.startswith("["):
        return f"-D{key}={text}"
    if text.startswith("meshtastic_") or text in {"true", "false"} or is_number_like(text):
        return f"-D{key}={text}"

    escaped = text.replace("'", "'\\''")
    return f"-D{key}='{escaped}'"


def parse_user_specs(path: Path) -> str:
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    defaults = raw.get("DEFAULTS")
    if not isinstance(defaults, dict):
        return ""

    flags = [stringify_spec(str(key), value) for key, value in defaults.items()]
    return " ".join(flag for flag in flags if flag)


def detect_mtjson_support(source_dir: Path) -> bool:
    for pattern in ("*.py", "*.sh"):
        for file_path in source_dir.rglob(pattern):
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "mtjson" in text:
                return True
    return False


def build_once(
    *,
    source_dir: Path,
    pio_target: str,
    build_dir: Path,
    build_flags: str,
    targets: Iterable[str],
) -> None:
    env = os.environ.copy()
    env["PLATFORMIO_BUILD_DIR"] = str(build_dir)
    if build_flags:
        env["PLATFORMIO_BUILD_FLAGS"] = build_flags

    command = ["pio", "run", "-d", str(source_dir), "-e", pio_target]
    for target in targets:
        command.extend(["-t", target])

    run_command(command, cwd=source_dir, env=env)


def maybe_convert_hex_to_uf2(source_dir: Path, build_dir: Path) -> None:
    uf2_files = list(build_dir.rglob("*.uf2"))
    if uf2_files:
        print(f"UF2 already exists for {build_dir}, conversion skipped")
        return

    hex_files = sorted(build_dir.rglob("*.hex"))
    if not hex_files:
        print(f"warning: no .hex files found in {build_dir}")
        return

    uf2conv = source_dir / "bin" / "uf2conv.py"
    if not uf2conv.exists():
        print(f"warning: {uf2conv} not found, cannot convert HEX->UF2")
        return

    first_hex = hex_files[0]
    output_uf2 = first_hex.with_suffix(".uf2")
    command = [
        sys.executable,
        str(uf2conv),
        str(first_hex),
        "-c",
        "-o",
        str(output_uf2),
        "-f",
        "0xADA52840",
    ]
    run_command(command, cwd=source_dir, env=os.environ.copy())


def copy_artifacts(build_dirs: Iterable[Path], destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for build_dir in build_dirs:
        if not build_dir.exists():
            continue
        for file_path in build_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if not file_path.name.endswith(ARTIFACT_SUFFIXES):
                continue
            target = destination / file_path.name
            shutil.copy2(file_path, target)
            copied += 1
    return copied


def detect_chip(pio_target: str) -> str:
    lowered = pio_target.lower()
    if "esp32s3" in lowered or "_s3" in lowered or "-s3" in lowered:
        return "esp32s3"
    if "esp32c3" in lowered or "_c3" in lowered or "-c3" in lowered:
        return "esp32c3"
    if "esp32c6" in lowered or "_c6" in lowered or "-c6" in lowered:
        return "esp32c6"
    return ""


def detect_flash_size(flags: str) -> str:
    lowered = flags.lower()
    if "16mb" in lowered:
        return "16MB"
    if "8mb" in lowered:
        return "8MB"
    return "4MB"


def write_metadata(
    *,
    output_dir: Path,
    build_name: str,
    version_label: str,
    device_name: str,
    device_type: str,
    pio_target: str,
    build_flags: str,
    build_notes: str,
    build_date: str,
) -> None:
    device_dir = output_dir / build_name
    version_dir = device_dir / version_label
    device_dir.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(parents=True, exist_ok=True)

    device_info = {
        "name": device_name,
        "type": device_type,
        "pio_target": pio_target,
        "chip": detect_chip(pio_target),
        "flashSize": detect_flash_size(build_flags),
    }
    ver_info = {
        "version": version_label,
        "date": build_date,
        "pio_target": pio_target,
    }
    if build_notes:
        ver_info["notes"] = build_notes
    if build_flags:
        ver_info["build_flags"] = build_flags

    (device_dir / "device.info").write_text(
        json.dumps(device_info, ensure_ascii=True),
        encoding="utf-8",
    )
    (version_dir / "ver.info").write_text(
        json.dumps(ver_info, ensure_ascii=True),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    user_specs_file = Path(args.user_specs_file).resolve() if args.user_specs_file else None

    if not source_dir.exists():
        raise FileNotFoundError(f"source-dir does not exist: {source_dir}")

    build_date = args.build_date.strip() or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    user_specs_flags = ""
    if user_specs_file:
        if user_specs_file.exists():
            user_specs_flags = parse_user_specs(user_specs_file)
            if user_specs_flags:
                print(f"user specs flags: {user_specs_flags}")
        else:
            print(f"warning: user specs file not found: {user_specs_file}")

    merged_flags = " ".join(
        flag for flag in (user_specs_flags, args.build_flags.strip()) if flag
    ).strip()
    supports_mtjson = detect_mtjson_support(source_dir)
    print(f"mtjson support: {supports_mtjson}")

    run_token = f"{int(time.time())}_{os.getpid()}"
    build_roots: list[Path] = []

    main_build_dir = source_dir / ".pio" / f"build_{run_token}" / args.build_name
    build_targets: list[str] = []
    if supports_mtjson:
        build_targets.append("mtjson")
    if args.pio_build_target:
        build_targets.append(args.pio_build_target)

    build_once(
        source_dir=source_dir,
        pio_target=args.pio_target,
        build_dir=main_build_dir,
        build_flags=merged_flags,
        targets=build_targets,
    )
    build_roots.append(main_build_dir)

    if args.device_type.lower() == "esp32" and not supports_mtjson:
        fs_build_dir = source_dir / ".pio" / f"build_{run_token}_fs" / args.build_name
        build_once(
            source_dir=source_dir,
            pio_target=args.pio_target,
            build_dir=fs_build_dir,
            build_flags=merged_flags,
            targets=["buildfs"],
        )
        build_roots.append(fs_build_dir)

    if args.device_type.lower() == "nrf52":
        maybe_convert_hex_to_uf2(source_dir, main_build_dir)

    version_dir = output_dir / args.build_name / args.version_label
    copied = copy_artifacts(build_roots, version_dir)
    if copied == 0:
        raise RuntimeError("No build artifacts were found after successful build")

    write_metadata(
        output_dir=output_dir,
        build_name=args.build_name,
        version_label=args.version_label,
        device_name=args.device_name,
        device_type=args.device_type,
        pio_target=args.pio_target,
        build_flags=merged_flags,
        build_notes=args.build_notes.strip(),
        build_date=build_date,
    )

    print(
        json.dumps(
            {
                "build_name": args.build_name,
                "pio_target": args.pio_target,
                "copied_artifacts": copied,
                "output": str(version_dir),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
