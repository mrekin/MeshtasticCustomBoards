# trunk-ignore-all(black)
import argparse
import configparser
import json
import os
import re

my_args = []
files = []
filledSections = []

def init():
    parser = argparse.ArgumentParser(description='Args parser')
    parser.add_argument('-d','--dir', type=str, default='.', help='Path to directory')
    parser.add_argument('-r','--recurcive',  action=argparse.BooleanOptionalAction, help='Recurcieve search')
    parser.add_argument('-m','--mask', type=str, default='.*\\.ini', help='PyRegex for file filtering by name. Can be used with `-e` option')
    parser.add_argument('-e','--extention', type=str, default='.ini', help='List of file extentions for file filtering. Comma separated. Can be used with `-m` option')
    parser.add_argument('-k','--keymask', type=str, default=r'.*', help='PyRegex for config key filtering')
    parser.add_argument('-s','--resolve', action=argparse.BooleanOptionalAction, help='Resolve variables in values')
    parser.add_argument('-a','--arguments',action=argparse.BooleanOptionalAction, help='Try parse param value as arguments, will try to represent string value as groups list or args')
    parser.add_argument('-p','--parammask',type=str, default=r'.*', help='PyRegex for config value filtering')
    parser.add_argument('-g','--groups',type=str, default=None, help='List of args groups for filtering, comma separated. Use with `-a`. Example: `D,I,W`')
    parser.add_argument('-j','--json',action=argparse.BooleanOptionalAction, help='Format Json output')
    parser.add_argument('-b','--board',action=argparse.BooleanOptionalAction, help='Resolve board sections and find corresponding JSON files in boards directory')
    parser.add_argument('-c','--compact',action=argparse.BooleanOptionalAction, help='Output flat key-value pairs with dot-notation path as key')
    parser.add_argument('--sectionmask', type=str, default=r'env:.*', help='PyRegex for section filtering')

    global my_args
    my_args = parser.parse_args()

def searchIni():
    flist = []
    boards_dir = None
    pattern = re.compile(my_args.mask)
    for address, _dirs, files in os.walk(my_args.dir, topdown=True if my_args.recurcive else False, onerror=None, followlinks=False):
        if my_args.board and not boards_dir and 'boards' in _dirs:
            boards_dir = os.path.join(address, 'boards')

        for file in files:
            if pattern.match(file):
                flist.append(f'{address}/{file}')
    return flist, boards_dir

def resolveBoardSection(board_name, boards_dir):
    """Resolve board section by finding corresponding JSON file"""
    if boards_dir:
        board_json_path = os.path.join(boards_dir, f"{board_name}.json")
        if os.path.exists(board_json_path):
            try:
                with open(board_json_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check pio_boards.json
    pio_boards_path = os.path.join(script_dir, 'pio_boards.json')
    if os.path.exists(pio_boards_path):
        try:
            with open(pio_boards_path, 'r') as f:
                boards = json.load(f)
                for board in boards:
                    if board.get('id') == board_name:
                        return board
        except (json.JSONDecodeError, IOError):
            pass

    # Check frameworks_boards.json
    frameworks_boards_path = os.path.join(script_dir, 'frameworks_boards.json')
    if os.path.exists(frameworks_boards_path):
        try:
            with open(frameworks_boards_path, 'r') as f:
                boards = json.load(f)
                for board in boards:
                    if board.get('id') == board_name:
                        return board
        except (json.JSONDecodeError, IOError):
            pass

    return None

def parseIniToDict(files):
    """Parse ini files to dict structure"""
    config = configparser.ConfigParser(inline_comment_prefixes=';')
    for file in files:
        config.read(file)

    result = {}
    sections = config.sections()

    for section in sections:
        result[section] = {}
        for key in config[section]:
            result[section][key] = config[section][key]

    return result, config

def infillDict(config_dict, section, filledSections):
    """Fill dict recursively by parent sections via extends param"""
    if section in filledSections:
        return config_dict

    if 'extends' in config_dict.get(section, {}):
        # Parse multiple parents separated by comma (left to right priority)
        parents = [p.strip() for p in config_dict[section]['extends'].split(',')]
        for parent in parents:
            if parent in config_dict:
                infillDict(config_dict, parent, filledSections)
                # Copy keys from parent (later parents override earlier ones)
                for key in config_dict[parent]:
                    if key not in config_dict[section]:
                        config_dict[section][key] = config_dict[parent][key]

    filledSections.append(section)
    return config_dict

def setNestedValue(obj, path, value):
    """Set value in nested dict by dot-separated path"""
    parts = path.split('.')
    current = obj
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value
    return obj

def getNestedValue(obj, path, default=None):
    """Get value from nested dict by dot-separated path"""
    parts = path.split('.')
    current = obj
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current

def resolveVarsInDict(value, config_dict, section):
    """Resolve variables in value string, supports nested dict access"""
    resolved = True
    value = value.replace("\n", " ")
    var_pattern = re.compile(r'\${([^{}]+)}')

    for var in re.finditer(var_pattern, value):
        var_path = var.group(1)
        parts = var_path.split('.')

        resolved_value = None
        current = config_dict

        # First try to resolve as section.key.path
        if parts[0] in config_dict:
            if len(parts) > 1:
                # section.key.path -> access nested value in section
                nested_path = '.'.join(parts[1:])
                resolved_value = getNestedValue(config_dict[parts[0]], nested_path)
            else:
                resolved_value = config_dict[parts[0]]
        else:
            # Try to resolve from current section
            resolved_value = getNestedValue(config_dict.get(section, {}), var_path)

            # If not found, try global search across all sections
            if resolved_value is None:
                for sect_name, sect_data in config_dict.items():
                    if var_path in sect_data:
                        resolved_value = sect_data[var_path]
                        break
                    else:
                        nested_val = getNestedValue(sect_data, var_path)
                        if nested_val is not None:
                            resolved_value = nested_val
                            break

        if resolved_value is not None:
            if isinstance(resolved_value, (dict, list)):
                resolved = False
            else:
                resolved_value = str(resolved_value).strip().replace("\n", " ")
                value = value.replace(var.group(0), resolved_value)
        else:
            resolved = False

    return value

def resolveAll(config_dict, boards_dir):
    """Resolve all variables and boards in config dict"""
    filledSections = []

    # First pass: infill extends
    for section in list(config_dict.keys()):
        infillDict(config_dict, section, filledSections)

    # Second pass: resolve boards (-b flag)
    if my_args.board:
        for section in config_dict:
            if 'board' in config_dict[section]:
                board_name = config_dict[section]['board']
                board_data = resolveBoardSection(board_name, boards_dir)
                if board_data:
                    # Store board data under board name
                    config_dict[section]['board'] = {
                        board_name: board_data
                    }

    # Third pass: resolve variables (-s flag)
    if my_args.resolve:
        max_iterations = 10
        for iteration in range(max_iterations):
            changed = False
            for section in config_dict:
                for key in list(config_dict[section].keys()):
                    value = config_dict[section][key]
                    if isinstance(value, str):
                        resolved = resolveVarsInDict(value, config_dict, section)
                        if resolved != value:
                            config_dict[section][key] = resolved
                            changed = True
            if not changed:
                break

    return config_dict

def flattenDict(d, prefix=''):
    """Flatten dict to dot-notation keys and values"""
    result = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(flattenDict(v, full_key))
        else:
            result[full_key] = v
    return result

def keyMatchesInNested(key_pattern, value):
    """Check if key pattern matches any nested keys in dict value"""
    if not isinstance(value, dict):
        return False
    flattened = flattenDict(value)
    for key in flattened.keys():
        if re.match(key_pattern, key):
            return True
    return False

def valueMatchesInNested(value_pattern, value):
    """Check if value pattern matches any nested values in dict"""
    if not isinstance(value, dict):
        val_str = str(value)
        return re.match(value_pattern, val_str) is not None
    flattened = flattenDict(value)
    for val in flattened.values():
        val_str = str(val)
        if re.match(value_pattern, val_str):
            return True
    return False

def filterNestedDict(value, key_pattern, value_pattern):
    """Filter nested dict to only include matching keys/values"""
    if not isinstance(value, dict):
        return valueMatchesInNested(value_pattern, value)

    result = {}
    for k, v in value.items():
        # Check if this key matches
        key_match = re.match(key_pattern, k)
        # Check if this value matches (or has nested matching values)
        val_match = valueMatchesInNested(value_pattern, v)

        # Both key AND value must match for non-dict values
        # For dict values, key must match and we recurse
        if key_match:
            if isinstance(v, dict):
                # For dict values, recurse - nested filtering will check both key+value
                nested = filterNestedDict(v, key_pattern, value_pattern)
                if nested is not None and nested != {}:
                    result[k] = nested
            elif val_match:
                # For non-dict values, both key and value must match
                result[k] = v
        elif isinstance(v, dict):
            # Key doesn't match, but check nested for any matches
            nested = filterNestedDict(v, key_pattern, value_pattern)
            if nested is not None and nested != {}:
                result[k] = nested

    return result if result != {} else None

def filterData(config_dict):
    """Filter config dict by patterns"""
    cfg = {}
    key_pattern = re.compile(my_args.keymask)
    section_pattern = re.compile(my_args.sectionmask)
    value_pattern = re.compile(my_args.parammask)

    for section in config_dict:
        if not re.match(section_pattern, section):
            continue

        cfg[section] = {}
        for key in config_dict[section]:
            val = config_dict[section][key]

            # Check key pattern - also check nested keys for dict values
            key_match = re.match(key_pattern, key) or keyMatchesInNested(key_pattern, val)
            if not key_match:
                continue

            if my_args.arguments and isinstance(val, str):
                cmd = argparse.ArgumentParser()
                if my_args.groups:
                    for g in my_args.groups.strip().split(','):
                        cmd.add_argument(f"-{g.strip()}", action=argparse._AppendAction, default=[])
                args, unknown = cmd.parse_known_args(val.split())
                val = vars(args)
                val['unknown'] = unknown

            if my_args.arguments and isinstance(val, dict):
                # Only process if this looks like argparse result (all values are lists)
                # Skip for non-list dicts like board data
                if all(isinstance(v, list) for v in val.values()):
                    keys = set(val.keys())
                    for k in keys:
                        kval = set(val[k])
                        for v in val[k]:
                            if not re.match(value_pattern, v):
                                kval.discard(v)
                        if len(kval) == 0:
                            val.pop(k)
                        else:
                            val[k] = list(kval)
                    if val != {}:
                        cfg[section][key] = val
                else:
                    # Not an argparse result dict, use regular dict filtering
                    filtered = filterNestedDict(val, key_pattern, value_pattern)
                    if filtered:
                        cfg[section][key] = filtered
            elif isinstance(val, dict):
                # For dict values, filter nested content by both key and value patterns
                filtered = filterNestedDict(val, key_pattern, value_pattern)
                if filtered:
                    cfg[section][key] = filtered
            else:
                # For non-dict values, check both key and value match
                val_str = str(val)
                if re.match(value_pattern, val_str):
                    cfg[section][key] = val

    # Remove empty sections
    sections = list(cfg.keys())
    for section in sections:
        if cfg[section] == {}:
            cfg.pop(section)

    return cfg

def flattenFilteredData(filtered_dict):
    """Convert filtered dict to flat key-value pairs with full path as key"""
    result = {}
    for section, data in filtered_dict.items():
        section_prefix = section
        for key, value in data.items():
            full_path = f"{section_prefix}.{key}"
            if isinstance(value, dict):
                flattened = flattenDict(value)
                for nested_key, nested_value in flattened.items():
                    result[f"{full_path}.{nested_key}"] = nested_value
            else:
                result[full_path] = value
    return result

if __name__ == "__main__":
    init()
    files, boards_dir = searchIni()
    config_dict, _ = parseIniToDict(files)
    config_dict = resolveAll(config_dict, boards_dir)
    cfg = filterData(config_dict)

    if my_args.compact:
        cfg = flattenFilteredData(cfg)

    if my_args.json:
        res = json.dumps(cfg, indent=4, sort_keys=True)
    else:
        res = json.dumps(cfg)
    print(res)
