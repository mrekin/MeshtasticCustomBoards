#!/usr/bin/env python3
"""
Generate pinout_table.json from variant.h files.

Usage:
    python3 generate_pinout.py [-t template.json] [variants_directory] [output_file]

Arguments:
    -t template.json: JSON file with defines structure (default: none)
    variants_directory: Path to variants directory (default: ./variants)
    output_file: Output JSON file (default: pinout_table.json)

Output:
    Creates pinout_table.json in current directory

Examples:
    python3 generate_pinout.py /path/to/meshtastic/variants
    python3 generate_pinout.py -t defines_structure.json /path/to/meshtastic/variants
    python3 generate_pinout.py -t template.json ./variants output.json
"""

import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime


def find_variant_h_files(variants_dir):
    """Find all variant.h files and platformio.ini files in the variants directory."""
    variants_path = Path(variants_dir)
    if not variants_path.exists():
        raise FileNotFoundError(f"Variants directory not found: {variants_dir}")

    # Find all variant.h files
    variant_files = list(variants_path.rglob("variant.h"))

    # Find all platformio.ini files
    platformio_files = list(variants_path.rglob("platformio.ini"))

    print(f"📁 Found {len(variant_files)} variant.h files and {len(platformio_files)} platformio.ini files")

    return variant_files, platformio_files


def extract_pins_from_arduino(pins_file):
    """Extract pin definitions from pins_arduino.h file.

    Parses patterns like:
        static const uint8_t MISO = 39;
        static const uint8_t MOSI = 40;
        const int RX = 5;
    """
    pins = {}
    try:
        with open(pins_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Match: [static] [const] <type> NAME = value;
        # Type can be: uint8_t, int, unsigned char, etc.
        # Pattern matches: const, uint8_t, int, unsigned long, etc.
        pattern = r'(?:static\s+)?(?:const\s+)?(\w+(?:\s+\w+)?)\s+(\w+)\s*=\s*(\d+)\s*;'

        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                var_type = match.group(1)
                name = match.group(2)
                value = match.group(3)
                pins[name] = value

        if pins:
            print(f"    📌 Found {len(pins)} pins in {pins_file.name}")

    except Exception as e:
        print(f"⚠️  Error reading {pins_file}: {e}")

    return pins


def extract_defines_from_file(file_path, pins_arduino=None):
    """Extract all #define statements from a variant.h file.

    Args:
        file_path: Path to variant.h file
        pins_arduino: Optional dict of pin values from pins_arduino.h
    """
    defines = {}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Match #define statements
        # Pattern: #define NAME value
        pattern = r'^\s*#\s*define\s+(\w+)\s+(.+?)\s*(?://.*|/\*.*\*/)?$'

        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                name = match.group(1)
                value = match.group(2).strip()
                # Remove trailing comments from value
                value = re.sub(r'\s*//.*$', '', value).strip()
                value = re.sub(r'\s*/\*.*\*/\s*$', '', value).strip()

                # Resolve references to pins_arduino.h constants
                # If value is a name that exists in pins_arduino, substitute it
                if pins_arduino and value in pins_arduino:
                    value = pins_arduino[value]

                defines[name] = value

    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")

    return defines


def find_variant_aliases(platformio_files, variants_dir):
    """Find variant aliases from platformio.ini files."""
    aliases = {}
    env_to_variant = {}  # Map env names to variant directories

    print(f"\n🔍 Looking for variant aliases in platformio.ini files...")

    # First pass: map env names to variant directories
    for platformio_file in platformio_files:
        try:
            ini_dir = platformio_file.parent
            variant_h = ini_dir / 'variant.h'

            if variant_h.exists():
                # This directory has variant.h
                relative_path = platformio_file.relative_to(variants_dir)
                variant_name = str(relative_path.parent)
                env_to_variant[variant_name] = variant_name

        except Exception as e:
            pass

    # Second pass: find aliases - directories without variant.h that reference other variants
    for platformio_file in platformio_files:
        try:
            with open(platformio_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check if this directory has variant.h
            ini_dir = platformio_file.parent
            if (ini_dir / 'variant.h').exists():
                continue  # Skip directories with their own variant.h

            # Get the directory path (this will be our alias name)
            relative_path = platformio_file.relative_to(variants_dir)
            alias_dir_path = str(relative_path.parent)  # e.g., "nrf52840/diy/nrf52_promicro_diy_tcxo_ru"

            # Find all [env:...] sections and check what they reference
            env_pattern = r'\[env:([^\]]+)\]'
            variant_ref = None

            for match in re.finditer(env_pattern, content):
                env_name = match.group(1)

                # Get the environment section content
                section_start = match.end()
                next_section = content.find('\n[', section_start)
                if next_section == -1:
                    section_content = content[section_start:]
                else:
                    section_content = content[section_start:next_section]

                # Look for -I variants/xxx/yyy in build_flags
                include_pattern = r'-I\s+variants/([^\s]+)'
                include_match = re.search(include_pattern, section_content)

                if include_match:
                    variant_ref = include_match.group(1)
                    break  # Found the referenced variant

            if variant_ref and variant_ref != alias_dir_path:
                # This directory is an alias to variant_ref
                if variant_ref not in aliases:
                    aliases[variant_ref] = []
                if alias_dir_path not in aliases[variant_ref]:
                    aliases[variant_ref].append(alias_dir_path)

        except Exception as e:
            pass  # Skip errors in platformio.ini parsing

    if aliases:
        print(f"  Found {len(aliases)} base variants with aliases:")
        for base, alias_list in sorted(aliases.items()):
            print(f"    {base} <- {', '.join(alias_list)}")
    else:
        print(f"  No aliases found")

    return aliases


def load_defines_template(template_file):
    """Load defines structure from JSON template file."""
    if not template_file:
        return None

    template_path = Path(template_file)
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build lookup dictionaries for fast searching
    # Structure: {define_name: (category_type, subcategory)}
    pin_lookup = {}
    config_lookup = {}

    all_defines = data.get('all_defines', {})

    # Process pins categories
    pins = all_defines.get('pins', {})
    for subcategory, define_list in pins.items():
        for define_name in define_list:
            pin_lookup[define_name] = subcategory

    # Process config categories
    config = all_defines.get('config', {})
    for subcategory, define_list in config.items():
        for define_name in define_list:
            config_lookup[define_name] = subcategory

    print(f"  Loaded {len(pin_lookup)} pin defines and {len(config_lookup)} config defines from template")

    return {
        'pins': pin_lookup,
        'config': config_lookup
    }


def categorize_with_template(define_name, define_value, template):
    """Categorize a define using template lookup.

    Returns ('pins', subcategory) or ('config', subcategory) or None.
    None means not found in template - should go to config/other.
    """
    if not template:
        return None  # No template - all to config/other

    # Try pin lookup first
    if define_name in template['pins']:
        return ('pins', template['pins'][define_name])

    # Try config lookup
    if define_name in template['config']:
        return ('config', template['config'][define_name])

    # Not found in template - goes to config/other
    return None


def generate_pinout_table(variants_dir, template=None):
    """Generate the complete pinout table JSON structure.

    Args:
        variants_dir: Path to variants directory
        template: Optional template lookup dict from load_defines_template()
    """

    print(f"\n{'='*60}")
    print("🔍 Analyzing variant.h files...")
    print('='*60)

    variant_files, platformio_files = find_variant_h_files(variants_dir)
    aliases = find_variant_aliases(platformio_files, variants_dir)

    # Structure: flat list with variant name as key
    result = {
        "metadata": {
            "total_variants": 0,
            "generated_date": datetime.now().isoformat(),
            "format_version": "2.0",
            "source_dir": str(variants_dir)
        },
        "variants": {}
    }

    # Store all variants flat - variant name as key
    all_variants = {}

    for variant_file in variant_files:
        # Extract family and board name from path
        relative_path = variant_file.relative_to(variants_dir)
        parts = list(relative_path.parts)

        if len(parts) < 2:
            continue

        family = parts[0]
        board = '/'.join(parts[1:]).replace('/variant.h', '')

        # Use just the last part as variant name (for flat structure)
        # parts = ['esp32', 'tbeam_v07', 'variant.h']
        # We want 'tbeam_v07' as variant_name
        variant_name = parts[-2] if len(parts) >= 2 and parts[-1] == 'variant.h' else board

        # Look for pins_arduino.h in the same directory
        variant_dir = variant_file.parent
        pins_arduino_file = variant_dir / 'pins_arduino.h'
        pins_arduino = None

        if pins_arduino_file.exists():
            pins_arduino = extract_pins_from_arduino(pins_arduino_file)

        # Extract defines
        defines = extract_defines_from_file(variant_file, pins_arduino=pins_arduino)

        # Separate pins (by category) from config (by category) and other
        pins = defaultdict(dict)
        config = defaultdict(dict)
        other = {}

        for define_name, define_value in defines.items():
            # Try template lookup first
            category_result = categorize_with_template(define_name, define_value, template)

            if category_result:
                # Found in template
                cat_type, cat_name = category_result
                if cat_type == 'pins':
                    pins[cat_name][define_name] = define_value
                else:  # config
                    config[cat_name][define_name] = define_value
            else:
                # Not found in template or no template - goes to other
                other[define_name] = define_value

        # Create variant entry
        variant_info = {
            "file": str(relative_path),
            "board": board,
            "family": family,
            "pins": dict(pins),
            "config": dict(config),
            "other": other
        }

        # Store with variant name as key
        all_variants[variant_name] = variant_info

        # Progress indicator
        total_pins = sum(len(cat_pins) for cat_pins in pins.values())
        total_config = sum(len(cat_cfg) for cat_cfg in config.values())
        total_other = len(other)
        print(f"  ✓ {family}/{board}: {total_pins} pins in {len(pins)} categories, {total_config} config in {len(config)} categories, {total_other} other")

    # Add aliases
    if aliases:
        print(f"\n  📝 Adding aliases...")
        for base_variant_path, alias_list in aliases.items():
            # base_variant_path is like "nrf52840/diy/nrf52_promicro_diy_tcxo"
            # Extract just the board name (last part)
            base_parts = base_variant_path.split('/')
            base_board = base_parts[-1]  # Last part: "nrf52_promicro_diy_tcxo"
            base_family = base_parts[0] if len(base_parts) > 1 else None

            # Find the base variant in all_variants
            if base_board in all_variants:
                base_info = all_variants[base_board]
                # Create entries for each alias
                for alias_name in alias_list:
                    # alias_name is like "nrf52840/diy/nrf52_promicro_diy_tcxo_ru"
                    # Extract just the last part as variant name
                    alias_parts = alias_name.split('/')
                    alias_variant_name = alias_parts[-1]  # "nrf52_promicro_diy_tcxo_ru"
                    alias_family = alias_parts[0] if len(alias_parts) > 1 else base_info['family']

                    # Create alias variant info
                    alias_info = {
                        "file": base_info["file"],  # Points to the actual variant.h file
                        "board": alias_name,
                        "family": alias_family,
                        "is_alias": True,
                        "alias_of": base_board,
                        "pins": base_info["pins"],
                        "config": base_info["config"]
                    }

                    # Add with variant name as key
                    all_variants[alias_variant_name] = alias_info

                    print(f"    ✓ {alias_variant_name} -> {base_board}")

    result["variants"] = all_variants
    result["metadata"]["total_variants"] = len(variant_files)
    result["metadata"]["total_variants_including_aliases"] = len(all_variants)

    # Calculate statistics
    families_in_variants = {}
    alias_count = 0
    for var_name, var_info in all_variants.items():
        family = var_info['family']
        if family not in families_in_variants:
            families_in_variants[family] = {'total': 0, 'aliases': 0}
        families_in_variants[family]['total'] += 1
        if var_info.get('is_alias', False):
            families_in_variants[family]['aliases'] += 1
            alias_count += 1

    families_count = len(families_in_variants)
    print(f"\n{'='*60}")
    print(f"📊 Statistics:")
    print(f"  Total variants with variant.h: {result['metadata']['total_variants']}")
    if aliases:
        print(f"  Total including aliases: {result['metadata']['total_variants_including_aliases']}")
        print(f"  Aliases found: {alias_count}")
    print(f"  MCU families: {families_count}")
    for family, stats in sorted(families_in_variants.items()):
        print(f"    {family}: {stats['total']} variants ({stats['total'] - stats['aliases']} + {stats['aliases']} aliases)")
    print('='*60)

    return result


def save_results(data, output_file="pinout_table.json"):
    """Save the generated pinout table to JSON file."""

    output_path = Path(output_file)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    file_size = output_path.stat().st_size / 1024  # Size in KB
    print(f"\n✅ Generated: {output_path} ({file_size:.1f} KB)")

    return output_path


def main():
    """Main entry point."""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Generate pinout_table.json from variant.h files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 %(prog)s /path/to/meshtastic/variants
  python3 %(prog)s -t defines_structure.json /path/to/meshtastic/variants
  python3 %(prog)s -t template.json ./variants output.json
        """
    )
    parser.add_argument('-t', '--template', type=str, default=None,
                        help='JSON file with defines structure (template)')
    parser.add_argument('variants_dir', type=str, nargs='?',
                        default='./variants',
                        help='Path to variants directory (default: ./variants)')
    parser.add_argument('output_file', type=str, nargs='?',
                        default='pinout_table.json',
                        help='Output JSON file (default: pinout_table.json)')

    args = parser.parse_args()

    template_file = args.template
    variants_dir = args.variants_dir
    output_file = args.output_file

    # Load template if provided
    template = None
    if template_file:
        print(f"📋 Loading template from: {template_file}")
        try:
            template = load_defines_template(template_file)
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"\n❌ Error parsing template JSON: {e}")
            sys.exit(1)
    else:
        print("⚠️  No template provided (-t flag). All defines will be categorized as 'other'.")

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Meshtastic Pinout Table Generator                  ║
╠══════════════════════════════════════════════════════════════╣
║  Source: {variants_dir:<50} ║
║  Output: {output_file:<50} ║
║  Template: {template_file or 'None':<49} ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        # Generate pinout table
        data = generate_pinout_table(variants_dir, template=template)

        # Save to file
        save_results(data, output_file)

        print(f"\n🎉 Done! You can now use the JSON file:")
        print(f"   jq '.variants.\"tbeam_v07\"' {output_file}")
        print(f"   jq '.variants | keys' {output_file}")
        print(f"   jq '.variants.\"nrf52_promicro_diy_tcxo_ru\"' {output_file}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print(f"\nUsage: python3 {sys.argv[0]} [-t template.json] <variants_directory> [output_file]")
        print(f"Example: python3 {sys.argv[0]} -t defines_structure.json ./variants pinout_table.json")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
