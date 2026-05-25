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
- `count` (optional): Exact number of expected matches (see below)

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
- `count` (optional): Exact number of expected matches (see below)

**Named Group Syntax:**
- Use `(?P<name>...)` to capture named groups
- Reference in replacement as `\g<name>` or `{name}`
- Can mix anonymous and named groups: `\1`, `\2`, etc.

**Behavior:**
- Uses Python `re` module
- Supports all Python regex features
- Invalid regex causes exit code 3
- Returns 0 changes if pattern not found (not an error)

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
- `count` (optional): Exact number of expected matches (see below)

**Behavior:**
- Searches for `insert_after` pattern in each line
- Inserts `line` after each matching line
- Empty parameters cause exit code 3
- Pattern not found causes exit code 3
- Inserts after ALL occurrences (use specific patterns for single insert)

## `count` field

Optional field for any patch type. Specifies the **exact** expected number of matches.

```yaml
- type: replace
  description: "Replace font encoding"
  count: 3
  search: "FREESANS_12PT_WIN1252"
  replace: "FREESANS_12PT_WIN1251"
```

**Rules:**
- For **single file**: `count` must match the number of matches in that file
- For **directory**: `count` must match the total number of matches across all files
- Files with 0 matches are not an error — only the aggregate total is checked
- If `count` doesn't match: error `count_mismatch`, exit code 3, no files are modified

**Use cases:**
- Safety net: ensure the patch targets the right number of occurrences
- CI/CD: catch unexpected changes in source files
- Validation: verify firmware structure hasn't changed

## Complete Example

```yaml
description: "Patch for Russian language support"

patches:
  - type: replace
    description: "Replace font encoding"
    count: 1
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
# Apply patch to a file
apply_patch.py path/to/file.h patches/INKHUD_RU.yml

# Apply patch to a directory
apply_patch.py path/to/dir patches/INKHUD_RU.yml

# Apply recursively with extension filter
apply_patch.py --recursive --extensions .cpp .h path/to/dir patches/INKHUD_RU.yml

# Apply with backup tag
apply_patch.py --backup inkhud_ru path/to/dir patches/INKHUD_RU.yml

# Dry run (show changes without modifying)
apply_patch.py --dry-run path/to/file.h patches/INKHUD_RU.yml

# Check if patch makes changes (useful for CI/CD)
apply_patch.py --error-no-changes path/to/file.h patches/INKHUD_RU.yml

# Rollback (latest backups)
apply_patch.py --rollback path/to/dir

# Rollback by backup ID
apply_patch.py --rollback inkhud_ru path/to/dir

# Rollback and delete backup files
apply_patch.py --rollback inkhud_ru --cleanup path/to/dir
```

## Exit Codes

- **0**: Success (patch applied)
- **1**: General error (invalid YAML, file not found)
- **2**: No changes made (only with `--error-no-changes` flag)
- **3**: Patch error (invalid regex, pattern not found, count mismatch)
- **4**: Filesystem error (permission denied, disk full)

## Best Practices

1. **Test first**: Always use `--dry-run` before applying patches
2. **Use `count`**: Add `count` to catch unexpected changes in source files
3. **Tag backups**: Use `--backup <id>` for targeted rollback
4. **Specific patterns**: Use specific `insert_after` patterns to avoid multiple inserts
5. **Validation**: Check JSON output for number of changes
6. **Version control**: Keep patches in version control
7. **Descriptions**: Use clear descriptions for each patch step

## Troubleshooting

### Pattern not found (exit code 3)
- Check that the `insert_after` pattern exists in the file
- Use `--dry-run` to see what would be changed
- Verify exact spacing and case sensitivity

### Count mismatch (exit code 3)
- Check `aggregate_counts` in JSON output to see actual match counts
- File may have changed since the patch was written
- Use `--dry-run` to validate before applying

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
