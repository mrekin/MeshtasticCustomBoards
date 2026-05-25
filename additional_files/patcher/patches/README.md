# Patches Directory

This directory contains YAML patch files for use with `apply_patch.py`.

## Patch Format

Each patch file must contain:
- `description`: Human-readable description of what the patch does
- `patches`: Array of patch objects to apply

## Patch Types

### 1. `replace`
Simple substring replacement.

```yaml
- type: replace
  description: "Replace encoding"
  search: "WIN1252"
  replace: "WIN1251"
```

**Parameters:**
- `search` (required): Substring to search for
- `replace` (required): Replacement string

**Behavior:**
- Replaces all occurrences of `search` with `replace`
- Supports multi-line replacements
- Returns 0 changes if `search` not found (not an error)

### 2. `regex_replace`
Replacement using regular expressions with support for named groups.

```yaml
- type: regex_replace
  description: "Update version"
  pattern: "#define VERSION (?P<major>\\d+)\\.(?P<minor>\\d+)"
  replacement: "#define VERSION \\g<major>.\\g<minor>"
```

**Parameters:**
- `pattern` (required): Regular expression pattern
- `replacement` (required): Replacement string

**Named Group Syntax:**
- Use `(?P<name>...)` to capture named groups
- Reference in replacement as `\g<name>` or `{name}`
- Can mix anonymous and named groups: `\1`, `\2`, etc.

**Behavior:**
- Uses Python `re` module
- Supports all Python regex features
- Invalid regex causes exit code 3
- Returns 0 changes if pattern not found (not an error)

**Examples:**

```yaml
# Extract and reformat version
- type: regex_replace
  pattern: "v(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)"
  replacement: "Version \\g<major>.\\g<minor> (patch \\g<patch>)"

# Rearrange components
- type: regex_replace
  pattern: "(?P<first>\\w+) (?P<second>\\w+)"
  replacement: "\\g<second>, \\g<first>"

# Use {name} syntax
- type: regex_replace
  pattern: "(?P<h1>[0-9A-F]{2}):(?P<h2>[0-9A-F]{2})"
  replacement: "0x{h1}, 0x{h2}"
```

### 3. `line_insert`
Insert a line after a pattern match.

```yaml
- type: line_insert
  description: "Add include"
  insert_after: "#include \"base.h\""
  line: "#include \"custom.h\""
```

**Parameters:**
- `insert_after` (required): Pattern to search for (insert after this line)
- `line` (required): Line content to insert

**Behavior:**
- Searches for `insert_after` pattern in each line
- Inserts `line` after each matching line
- Empty parameters cause exit code 3
- Pattern not found causes exit code 3
- Inserts after ALL occurrences (use specific patterns for single insert)

## Complete Example

```yaml
description: "Patch for Russian language support"

patches:
  - type: replace
    description: "Replace font encoding"
    search: "FREESANS_12PT_WIN1252"
    replace: "FREESANS_12PT_WIN1251"

  - type: regex_replace
    description: "Update version string"
    pattern: "#define VERSION \\d+\\.\\d+"
    replacement: "#define VERSION 2.0"

  - type: line_insert
    description: "Add Russian localization include"
    insert_after: "#include \"localization.h\""
    line: "#include \"localization_ru.h\""
```

## Usage

```bash
# Apply patch
apply_patch.py path/to/file.h patches/INKHUD_RU.yml

# Dry run (show changes without modifying)
apply_patch.py --dry-run path/to/file.h patches/INKHUD_RU.yml

# Check if patch makes changes (useful for CI/CD)
apply_patch.py --error-no-changes path/to/file.h patches/INKHUD_RU.yml

# Save JSON report to file
apply_patch.py path/to/file.h patches/INKHUD_RU.yml > report.json

# Save JSON report to file and also write to file
apply_patch.py --json-output report.json path/to/file.h patches/INKHUD_RU.yml
```

## Exit Codes

- **0**: Success (patch applied)
- **1**: General error (invalid YAML, file not found)
- **2**: No changes made (only with `--error-no-changes` flag)
- **3**: Patch error (invalid regex, pattern not found for line_insert)
- **4**: Filesystem error (permission denied, disk full)

## Best Practices

1. **Test first**: Always use `--dry-run` before applying patches
2. **Specific patterns**: Use specific `insert_after` patterns to avoid multiple inserts
3. **Backup**: Automatic backups are created with timestamps
4. **Validation**: Check JSON output for number of changes
5. **Version control**: Keep patches in version control
6. **Descriptions**: Use clear descriptions for each patch step

## Troubleshooting

### Pattern not found (exit code 3)
- Check that the `insert_after` pattern exists in the file
- Use `--dry-run` to see what would be changed
- Verify exact spacing and case sensitivity

### Invalid regex (exit code 3)
- Test regex patterns separately
- Remember to escape backslashes: `\\d` not `\d`
- Use `--dry-run` to validate before applying

### No changes made (exit code 2 with `--error-no-changes`)
- File already contains the changes
- Search patterns don't match anything
- Use JSON output to see which patches made 0 changes

### Filesystem errors (exit code 4)
- Check file permissions
- Verify disk space
- Ensure file is not locked by another process
