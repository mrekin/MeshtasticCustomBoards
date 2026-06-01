#!/usr/bin/env python3
"""PlatformIO build helper — extracted from Jenkinsfile.

Single-command build tool that handles:
  - Auto-detection of device metadata via inipio (cached)
  - Build flags preparation from user_specs YAML
  - Patch apply → build → patch rollback
  - Post-build steps (ESP32 buildfs, NRF52 HEX→UF2)
  - device.info / ver.info generation
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

INIPO_PATH = os.environ.get(
    'INIPO_PATH',
    'customBoards/additional_files/inipio.py'
)
PATCHER_PATH = os.environ.get(
    'PATCHER_PATH',
    'customBoards/additional_files/patcher/apply_patch.py'
)
PATCHES_DIR = os.environ.get(
    'PATCHES_DIR',
    'customBoards/additional_files/patcher/patches'
)
BUILD_PARAMS_DIR = os.environ.get(
    'BUILD_PARAMS_DIR',
    'customBoards/additional_files/buildParams'
)
CACHE_DIR = os.environ.get('PIO_BUILD_CACHE_DIR', '/tmp')


def get_unique_timestamp():
    now = datetime.now()
    return now.strftime('%Y%m%d_%H%M%S_') + f'{now.microsecond // 1000:03d}'


def stringify_spec(key, value):
    val = str(value)
    if (val.startswith('{') or
            val.lstrip('-').replace('.', '').isdigit() or
            val in ('true', 'false') or
            val.startswith('meshtastic_')):
        return f'-D{key}={val}'
    escaped = val.replace("'", "'\\''")
    return f"-D{key}='{escaped}'"


# ─── Inipio wrapper with caching ──────────────────────────────────

def _cache_path(tag):
    safe = tag.replace('/', '_')
    return Path(CACHE_DIR) / f'pio_build_cache_{safe}.json'


def _run_inipio(work_dir, extra_args):
    cmd = ['python3', INIPO_PATH, '-d', work_dir] + extra_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"inipio error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return None


def load_tag_metadata(tag, work_dir=None):
    _dir = work_dir or tag
    cache = _cache_path(tag)
    if cache.exists():
        try:
            with open(cache) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    meta = {}

    variant_dirs = _run_inipio(_dir, ['-a', '-s', '-k', 'build_flags', '-g', 'I,W', '-p', 'variants/.*'])
    meta['variant_dirs'] = variant_dirs or {}

    for dtype in ('esp32', 'nrf52840', 'rp2040'):
        data = _run_inipio(_dir, ['-r', '-j', '-s', '-p', f'.*{dtype}.*', '-k', r'^(?!.*filter.*)'])
        if data:
            meta.setdefault('device_types', {})[dtype] = list(data.keys())

    for pattern, name in [('.*8MB.*', 'flash_8mb'), ('.*16MB.*', 'flash_16mb')]:
        data = _run_inipio(_dir, ['-r', '-j', '-s', '-k', 'board_build.partitions', '-p', pattern])
        meta[name] = data or {}

    for pattern, name in [('.*esp32s3.*', 'esp32s3'), ('.*esp32c3.*', 'esp32c3'), ('.*esp32c6.*', 'esp32c6')]:
        data = _run_inipio(_dir, ['-r', '-j', '-s', '-p', pattern])
        meta[name] = data or {}

    mtjson_found = False
    tag_dir = Path(_dir)
    if tag_dir.is_dir():
        for root, _dirs, files in os.walk(tag_dir):
            for fn in files:
                if fn.endswith(('.py', '.sh')):
                    fp = os.path.join(root, fn)
                    try:
                        with open(fp, errors='ignore') as f:
                            if 'mtjson' in f.read():
                                mtjson_found = True
                                break
                    except OSError:
                        pass
            if mtjson_found:
                break
    meta['mtjson'] = mtjson_found

    try:
        with open(cache, 'w') as f:
            json.dump(meta, f)
    except OSError as e:
        print(f"Warning: cache write failed: {e}", file=sys.stderr)

    return meta


def resolve_device_type(target, meta):
    env = f'env:{target}'
    for dtype in ('esp32', 'nrf52840', 'rp2040'):
        dt_list = meta.get('device_types', {}).get(dtype, [])
        if env in dt_list:
            if dtype == 'nrf52840':
                return 'nrf52'
            return dtype
    if 'esp32' in target.lower():
        return 'esp32'
    if 'nrf' in target.lower():
        return 'nrf52'
    if 'rp2040' in target.lower() or 'rp2350' in target.lower():
        return 'rp2040'
    return 'unknown'


def resolve_variant_dir(target, meta):
    env = f'env:{target}'
    try:
        return meta['variant_dirs'][env]['build_flags']['I'][0]
    except (KeyError, TypeError, IndexError):
        return None


def resolve_chip(target, meta):
    env = f'env:{target}'
    if meta.get('esp32s3', {}).get(env):
        return 'esp32s3'
    if meta.get('esp32c3', {}).get(env):
        return 'esp32c3'
    if meta.get('esp32c6', {}).get(env):
        return 'esp32c6'
    return ''


def resolve_flash_size(target, meta):
    env = f'env:{target}'
    if meta.get('flash_16mb', {}).get(env):
        return '16MB'
    if meta.get('flash_8mb', {}).get(env):
        return '8MB'
    return '4MB'


# ─── Build flags preparation ──────────────────────────────────────

def prepare_build_flags(user_specs, device_flags):
    parts = []

    if user_specs:
        if '..' in user_specs or user_specs.startswith('/') or '~' in user_specs:
            print(f"Invalid user_specs path: '{user_specs}'", file=sys.stderr)
            return None
        specs_path = Path(BUILD_PARAMS_DIR) / user_specs
        if specs_path.exists():
            if yaml is None:
                print("Error: PyYAML required for user_specs parsing", file=sys.stderr)
                return None
            try:
                with open(specs_path) as f:
                    ydata = yaml.safe_load(f)
                defaults = ydata.get('DEFAULTS', {}) if ydata else {}
                if isinstance(defaults, dict):
                    parts.extend(stringify_spec(k, v) for k, v in defaults.items())
            except Exception as e:
                print(f"Warning: user_specs parse error: {e}", file=sys.stderr)
        else:
            print(f"Warning: user_specs not found: {specs_path}", file=sys.stderr)

    if device_flags:
        parts.append(device_flags)

    return ' '.join(parts) if parts else ''


# ─── Patch apply / rollback ──────────────────────────────────────

def apply_patches(build_name, patches, work_dir, variant_dir):
    if not patches:
        return True
    target_dir = os.path.join(work_dir, variant_dir)
    for patch_file in patches:
        patch_path = os.path.join(PATCHES_DIR, patch_file)
        print(f"Applying patch: {patch_file} -> {target_dir}")
        exit_code = subprocess.run(
            ['python3', PATCHER_PATH, '--backup', build_name, '--recursive', target_dir, patch_path],
        ).returncode
        if exit_code != 0:
            print(f"Patch failed: {patch_file} (exit {exit_code})", file=sys.stderr)
            return False
    return True


def rollback_patches(build_name, work_dir, variant_dir):
    if not variant_dir:
        return
    target_dir = os.path.join(work_dir, variant_dir)
    print(f"Rolling back patches for {build_name} -> {target_dir}")
    result = subprocess.run(
        ['python3', PATCHER_PATH, '--rollback', build_name, '--recursive', '--cleanup', target_dir],
        capture_output=True, text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"Warning: rollback failed (exit {result.returncode})", file=sys.stderr)


# ─── Build execution ─────────────────────────────────────────────

def run_build(target, build_name, build_flags, mtjson, pio_build_target, work_dir,
              max_retries=2):
    timestamp = get_unique_timestamp()
    build_dir = f'.pio/build_{timestamp}/{build_name}'

    env = os.environ.copy()
    if build_flags:
        env['PLATFORMIO_BUILD_FLAGS'] = build_flags
    env['PLATFORMIO_BUILD_DIR'] = build_dir

    cmd = ['pio', 'run', '-e', target]
    if mtjson:
        cmd.extend(['-t', 'mtjson'])
    if pio_build_target:
        cmd.extend(['-t', pio_build_target])

    print(f"Building: {' '.join(cmd)} (dir={build_dir})")
    for attempt in range(max_retries):
        exit_code = subprocess.run(cmd, cwd=work_dir, env=env).returncode
        if exit_code == 0:
            break
        if attempt < max_retries - 1:
            wait = 5 * (attempt + 1)
            print(f"Build failed (attempt {attempt + 1}/{max_retries}), retrying in {wait}s...")
            time.sleep(wait)
        else:
            break
    return exit_code, build_dir


def run_buildfs(target, work_dir):
    timestamp = get_unique_timestamp()
    build_dir = f'.pio/build_{timestamp}/buildfs'
    env = os.environ.copy()
    env['PLATFORMIO_BUILD_DIR'] = build_dir
    print(f"ESP32 buildfs for {target}")
    return subprocess.run(['pio', 'run', '--target', 'buildfs', '-e', target], cwd=work_dir, env=env).returncode


def convert_hex_to_uf2(build_dir, work_dir):
    try:
        import glob as g
        pattern = os.path.join(work_dir, build_dir, '**', '*.uf2')
        uf2_files = g.glob(pattern, recursive=True)
        if uf2_files:
            print(f"UF2 already exists: {uf2_files[0]}")
            return

        pattern = os.path.join(work_dir, build_dir, '**', '*.hex')
        hex_files = g.glob(pattern, recursive=True)
        if not hex_files:
            print(f"No HEX file found in {build_dir}", file=sys.stderr)
            return

        hex_file = hex_files[0]
        uf2_file = re.sub(r'\.hex$', '.uf2', hex_file)
        print(f"Converting {hex_file} -> {uf2_file}")
        subprocess.run(
            ['./bin/uf2conv.py', hex_file, '-c', '-o', uf2_file, '-f', '0xADA52840'],
            cwd=work_dir, check=False,
        )
    except Exception as e:
        print(f"Warning: HEX→UF2 conversion error: {e}", file=sys.stderr)


# ─── Info file generation ────────────────────────────────────────

def generate_device_info(build_name, device_name, device_type, target, chip, flash_size, output_dir):
    info = {
        'name': device_name,
        'type': device_type,
        'pio_target': target,
        'chip': chip,
        'flashSize': flash_size,
    }
    device_dir = Path(output_dir) / build_name
    device_dir.mkdir(parents=True, exist_ok=True)
    with open(device_dir / 'device.info', 'w') as f:
        json.dump(info, f, indent=2)


def generate_ver_info(build_name, target, tag, output_dir, build_date='', build_notes='',
                      build_flags='', latest_tag=''):
    version_dir = Path(output_dir) / build_name / tag
    version_dir.mkdir(parents=True, exist_ok=True)
    ver_file = version_dir / 'ver.info'

    existing = {}
    if ver_file.exists():
        try:
            with open(ver_file) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    info = existing.copy()
    info['version'] = tag
    info['pio_target'] = target
    if build_date:
        info['date'] = build_date
    if build_notes:
        info['notes'] = build_notes
    if build_flags:
        info['build_flags'] = build_flags
    if latest_tag:
        info['latestTag'] = latest_tag

    with open(ver_file, 'w') as f:
        json.dump(info, f, indent=2)


# ─── Main command: build ─────────────────────────────────────────

def cmd_build(args):
    work_dir = args.work_dir or args.tag
    meta = load_tag_metadata(args.tag, work_dir=work_dir)

    device_type = resolve_device_type(args.target, meta)
    if device_type == 'unknown':
        print(f"Warning: cannot determine device type for {args.target}", file=sys.stderr)

    mtjson = meta.get('mtjson', False)
    variant_dir = resolve_variant_dir(args.target, meta)
    chip = resolve_chip(args.target, meta)
    flash_size = resolve_flash_size(args.target, meta)

    patches = [p.strip() for p in args.patches.split(',')] if args.patches else []
    build_flags = prepare_build_flags(args.user_specs, args.device_flags)
    if build_flags is None:
        return 2

    # Apply patches
    if patches:
        if not variant_dir:
            print(f"Error: cannot resolve variant dir for {args.target}", file=sys.stderr)
            return 1
        if not apply_patches(args.build_name, patches, work_dir, variant_dir):
            return 1

    try:
        # Build
        exit_code, build_dir = run_build(
            args.target, args.build_name, build_flags,
            mtjson, args.pio_build_target, work_dir,
        )
        if exit_code != 0:
            print(f"Build FAILED for {args.build_name} (exit {exit_code})", file=sys.stderr)
            return 1

        # Post-build
        if device_type == 'esp32' and not mtjson:
            fs_exit = run_buildfs(args.target, work_dir)
            if fs_exit != 0:
                print(f"buildfs FAILED for {args.target} (exit {fs_exit})", file=sys.stderr)
                return 3

        if device_type == 'nrf52':
            convert_hex_to_uf2(build_dir, work_dir)

        # Generate info files
        if args.generate_info:
            output_dir = args.output_dir or os.environ.get('OUTPUT_DIR', 'output')
            generate_device_info(args.build_name, args.device_name, args.device_type, args.target, chip, flash_size, output_dir)
            generate_ver_info(
                args.build_name, args.target, args.tag, output_dir,
                build_date=args.build_date or '',
                build_notes=args.build_notes or '',
                build_flags=build_flags,
                latest_tag=args.latest_tag or '',
            )

    finally:
        # Rollback patches
        if patches:
            rollback_patches(args.build_name, work_dir, variant_dir)

    return 0


# ─── Generate info files only (no build) ─────────────────────────

def cmd_generate_info(args):
    meta = load_tag_metadata(args.tag)
    chip = resolve_chip(args.target, meta)
    flash_size = resolve_flash_size(args.target, meta)

    output_dir = args.output_dir or os.environ.get('OUTPUT_DIR', 'output')
    generate_device_info(args.build_name, args.device_name, args.device_type, args.target, chip, flash_size, output_dir)
    generate_ver_info(
        args.build_name, args.target, args.tag, output_dir,
        build_date=args.build_date or '',
        build_notes=args.build_notes or '',
        build_flags='',
        latest_tag=args.latest_tag or '',
    )
    return 0


# ─── CLI setup ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='PlatformIO build helper for Meshtastic firmware pipeline',
    )
    sub = parser.add_subparsers(dest='command')

    build = sub.add_parser('build', help='Build firmware (with optional patching)')
    build.add_argument('--tag', required=True, help='Git tag / version directory')
    build.add_argument('--work-dir', default='', help='Working directory for build (defaults to tag)')
    build.add_argument('--target', required=True, help='PlatformIO environment name')
    build.add_argument('--build-name', required=True, help='Build output name')
    build.add_argument('--device-name', default='', help='Device display name (from YAML)')
    build.add_argument('--device-type', default='', help='Device type: esp32/nrf52/rp2040 (from YAML)')
    build.add_argument('--user-specs', default='', help='User specs YAML filename')
    build.add_argument('--device-flags', default='', help='Additional build flags')
    build.add_argument('--patches', default='', help='Comma-separated patch filenames')
    build.add_argument('--pio-build-target', default='', help='Custom pio build target')
    build.add_argument('--generate-info', action='store_true', help='Generate device.info/ver.info')
    build.add_argument('--output-dir', default='', help='Output directory for info files')
    build.add_argument('--build-date', default='', help='Build date for ver.info')
    build.add_argument('--build-notes', default='', help='Build notes for ver.info')
    build.add_argument('--latest-tag', default='', help='Latest git tag for daily builds')

    gen = sub.add_parser('generate-info', help='Generate device.info/ver.info without building')
    gen.add_argument('--tag', required=True, help='Git tag / version directory')
    gen.add_argument('--target', required=True, help='PlatformIO environment name')
    gen.add_argument('--build-name', required=True, help='Build output name')
    gen.add_argument('--device-name', required=True, help='Device display name (from YAML)')
    gen.add_argument('--device-type', required=True, help='Device type: esp32/nrf52/rp2040 (from YAML)')
    gen.add_argument('--output-dir', default='', help='Output directory for info files')
    gen.add_argument('--build-date', default='', help='Build date for ver.info')
    gen.add_argument('--build-notes', default='', help='Build notes for ver.info')
    gen.add_argument('--latest-tag', default='', help='Latest git tag for daily builds')

    args = parser.parse_args()
    if args.command == 'build':
        sys.exit(cmd_build(args))
    elif args.command == 'generate-info':
        sys.exit(cmd_generate_info(args))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == '__main__':
    main()
