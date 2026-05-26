#!/usr/bin/env python3
"""
Variant code patcher for MeshtasticCustomBoards

Applies YAML-based patches to source files with support for:
- replace: Simple substring replacement
- regex_replace: Regex-based replacement with named groups
- line_insert: Insert lines after a pattern

Features:
- Dry-run mode for testing
- Backup creation with timestamps
- JSON reports to STDOUT
- Exit codes 0-4 for different scenarios
- --error-no-changes mode for CI/CD
- Directory mode with recursive traversal and extension filter
- Count limit per patch for safety
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class PatchApplier:
    """Main class for applying patches to files"""

    def __init__(self, dry_run: bool = False, error_no_changes: bool = False, backup_id: str = None):
        self.dry_run = dry_run
        self.error_no_changes = error_no_changes
        self.backup_id = backup_id
        self.patch_results: List[Dict[str, Any]] = []
        self.total_changes = 0

    def create_backup(self, file_path: Path, backup_id: str = None) -> Path:
        """Create a timestamped backup of the file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"{timestamp}_{backup_id}" if backup_id else timestamp
        backup_path = file_path.parent / f"{file_path.name}.backup_{suffix}"
        backup_path.write_bytes(file_path.read_bytes())
        return backup_path

    def collect_files(
        self, directory: Path, recursive: bool = False, extensions: List[str] = None
    ) -> List[Path]:
        """
        Collect files from a directory

        Args:
            directory: Directory to scan
            recursive: If True, scan subdirectories recursively
            extensions: Optional list of file extensions to include (e.g. ['.cpp', '.h'])

        Returns:
            Sorted list of file paths
        """
        pattern = "**/*" if recursive else "*"
        files = []
        for path in sorted(directory.glob(pattern)):
            if not path.is_file():
                continue
            if ".backup_" in path.name:
                continue
            if extensions and path.suffix not in extensions:
                continue
            files.append(path)
        return files

    def load_patch_yaml(self, patch_path: Path) -> Dict[str, Any]:
        """Load and validate patch YAML file"""
        import yaml

        try:
            with open(patch_path, "r", encoding="utf-8") as f:
                patch_data = yaml.safe_load(f)

            # Validate structure
            if not isinstance(patch_data, dict):
                raise ValueError("Patch YAML must be a dictionary")

            if "description" not in patch_data:
                raise ValueError("Patch must have a 'description' field")

            if "patches" not in patch_data:
                raise ValueError("Patch must have a 'patches' field")

            if not isinstance(patch_data["patches"], list):
                raise ValueError("'patches' must be a list")

            # Validate each patch
            for i, patch in enumerate(patch_data["patches"]):
                if not isinstance(patch, dict):
                    raise ValueError(f"Patch {i} must be a dictionary")

                if "type" not in patch:
                    raise ValueError(f"Patch {i} must have a 'type' field")

                patch_type = patch["type"]
                if patch_type not in ["replace", "regex_replace", "line_insert"]:
                    raise ValueError(
                        f"Patch {i}: Unknown type '{patch_type}'. "
                        "Supported types: replace, regex_replace, line_insert"
                    )

                if "count" in patch:
                    count_val = patch["count"]
                    if not isinstance(count_val, int) or count_val < 1:
                        raise ValueError(
                            f"Patch {i}: 'count' must be a positive integer, got {count_val}"
                        )

            return patch_data

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Patch file not found: {patch_path}") from e

    def apply_replace(
        self, content: str, search: str, replace: str
    ) -> Tuple[str, int]:
        """
        Apply a replace patch

        Args:
            content: File content
            search: Substring to search for
            replace: Replacement string

        Returns:
            Tuple of (new_content, count_of_replacements)
        """
        count = content.count(search)
        new_content = content.replace(search, replace)
        return new_content, count

    def apply_regex_replace(
        self, content: str, pattern: str, replacement: str
    ) -> Tuple[str, int]:
        r"""
        Apply a regex_replace patch with support for named groups

        Args:
            content: File content
            pattern: Regular expression pattern
            replacement: Replacement string (supports \g<name> or {name} for named groups)

        Returns:
            Tuple of (new_content, count_of_replacements)

        Raises:
            ValueError: If regex pattern is invalid
        """
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}") from e

        # Count matches
        matches = list(regex.finditer(content))
        count = len(matches)

        # Apply replacement
        new_content = regex.sub(replacement, content)

        return new_content, count

    def apply_line_insert(
        self, content: str, insert_after: str, line: str
    ) -> Tuple[str, int]:
        """
        Apply a line_insert patch (insert line after pattern)

        Args:
            content: File content
            insert_after: Pattern to search for (insert after this line)
            line: Line to insert

        Returns:
            Tuple of (new_content, count_of_insertions)

        Raises:
            ValueError: If insert_after pattern not found
        """
        if not insert_after:
            raise ValueError("insert_after parameter cannot be empty")

        if not line:
            raise ValueError("line parameter cannot be empty")

        # Split content into lines
        lines = content.split("\n")

        # Find pattern and insert after it
        new_lines = []
        count = 0

        for current_line in lines:
            new_lines.append(current_line)

            # Check if this line matches the pattern
            if insert_after in current_line:
                # Insert the new line after this one
                new_lines.append(line)
                count += 1

        if count == 0:
            raise ValueError(
                f"Pattern not found: insert_after line '{insert_after}' not found in file"
            )

        new_content = "\n".join(new_lines)
        return new_content, count

    @staticmethod
    def _parse_backup_name(name: str) -> Tuple[str, str, str]:
        """
        Parse backup filename into (original_name, timestamp, backup_id)

        Formats:
            file.h.backup_20260525_075216        → ('file.h', '20260525_075216', '')
            file.h.backup_20260525_075216_myid   → ('file.h', '20260525_075216', 'myid')
        """
        parts = name.split(".backup_")
        original_name = parts[0]
        suffix = parts[1] if len(parts) > 1 else ""
        # suffix is 'YYYYMMDD_HHMMSS' or 'YYYYMMDD_HHMMSS_id'
        timestamp = suffix[:15]  # YYYYMMDD_HHMMSS
        backup_id = suffix[16:] if len(suffix) > 15 else ""
        return original_name, timestamp, backup_id

    def find_backups(
        self, target: Path, recursive: bool = False, backup_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find .backup_* files for a target file or directory

        Args:
            target: File or directory to search for backups
            recursive: If True, search subdirectories (directory mode only)
            backup_id: If set, only return backups with this ID

        Returns:
            List of dicts with 'backup_path', 'original_path', 'timestamp', 'backup_id',
            sorted by timestamp descending (newest first)
        """
        backups = []

        if target.is_file():
            for backup_path in sorted(target.parent.glob(f"{target.name}.backup_*")):
                _, ts, bid = self._parse_backup_name(backup_path.name)
                if backup_id and bid != backup_id:
                    continue
                backups.append({
                    "backup_path": backup_path,
                    "original_path": target,
                    "timestamp": ts,
                    "backup_id": bid,
                })
        elif target.is_dir():
            glob_pattern = "**/*.backup_*" if recursive else "*.backup_*"
            for backup_path in sorted(target.glob(glob_pattern)):
                orig_name, ts, bid = self._parse_backup_name(backup_path.name)
                if backup_id and bid != backup_id:
                    continue
                backups.append({
                    "backup_path": backup_path,
                    "original_path": backup_path.parent / orig_name,
                    "timestamp": ts,
                    "backup_id": bid,
                })

        backups.sort(key=lambda b: b["timestamp"], reverse=True)
        return backups

    def rollback(
        self, target: Path, recursive: bool = False, cleanup: bool = False,
        rollback_id: str = None
    ) -> Dict[str, Any]:
        """
        Restore files from their latest backups

        Args:
            target: File or directory to rollback
            recursive: If True, search subdirectories (directory mode only)
            cleanup: If True, delete backup files after restoring
            rollback_id: If set, only restore backups with this ID

        Returns:
            Report dictionary
        """
        all_backups = self.find_backups(target, recursive, backup_id=rollback_id)

        if not all_backups:
            return {
                "success": False,
                "mode": "rollback",
                "target": str(target),
                "error": "No backup files found",
                "error_type": "no_backups",
                "exit_code": 1,
                "total_restored": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # Group by original file, pick latest backup for each
        latest = {}
        for b in all_backups:
            orig = str(b["original_path"])
            if orig not in latest:
                latest[orig] = b

        restored = []
        failed = []

        for orig_str, backup_info in latest.items():
            original_path = backup_info["original_path"]
            backup_path = backup_info["backup_path"]

            try:
                original_path.write_bytes(backup_path.read_bytes())
                print(f"Restored: {original_path} <- {backup_path.name}")
                restored.append({
                    "file": str(original_path),
                    "backup": str(backup_path),
                })

                if cleanup:
                    backup_path.unlink()

            except Exception as e:
                failed.append({
                    "file": str(original_path),
                    "backup": str(backup_path),
                    "error": str(e),
                })

        report = {
            "mode": "rollback",
            "target": str(target),
            "total_restored": len(restored),
            "restored_files": restored,
            "exit_code": 0 if not failed else 1,
            "success": len(restored) > 0 and len(failed) == 0,
            "timestamp": datetime.now().isoformat(),
        }

        if failed:
            report["failed_files"] = failed

        if cleanup:
            report["cleanup"] = True

        return report

    def _count_matches(self, content: str, patch: Dict[str, Any]) -> int:
        """
        Count how many times a patch would apply without modifying content

        Args:
            content: File content
            patch: Patch dictionary

        Returns:
            Number of matches found
        """
        patch_type = patch["type"]

        if patch_type == "replace":
            search = patch.get("search", "")
            return content.count(search) if search else 0

        elif patch_type == "regex_replace":
            pattern = patch.get("pattern", "")
            if not pattern:
                return 0
            try:
                regex = re.compile(pattern)
                return len(list(regex.finditer(content)))
            except re.error:
                return 0

        elif patch_type == "line_insert":
            insert_after = patch.get("insert_after", "")
            if not insert_after:
                return 0
            return sum(1 for line in content.split("\n") if insert_after in line)

        return 0

    def validate_counts_for_content(
        self, content: str, patches: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Validate count expectations against actual matches in content.
        Returns error string if mismatch found, None if all OK.
        """
        for i, patch in enumerate(patches):
            expected_count = patch.get("count")
            if expected_count is not None:
                actual_count = self._count_matches(content, patch)
                if actual_count != expected_count:
                    desc = patch.get("description", f"patch {i}")
                    return (
                        f"Count mismatch for {desc}: "
                        f"expected {expected_count}, found {actual_count}"
                    )
        return None

    def apply_patch(
        self, content: str, patch: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Apply a single patch to content

        Args:
            content: File content
            patch: Patch dictionary

        Returns:
            Tuple of (new_content, patch_result)
        """
        patch_type = patch["type"]
        description = patch.get("description", "")
        result = {
            "type": patch_type,
            "description": description,
            "success": False,
            "changes_count": 0,
            "changes_made": False,
        }

        try:
            new_content = content
            count = 0

            if patch_type == "replace":
                search = patch.get("search", "")
                replace_str = patch.get("replace", "")

                if not search:
                    raise ValueError("replace patch requires 'search' parameter")

                new_content, count = self.apply_replace(content, search, replace_str)

            elif patch_type == "regex_replace":
                pattern = patch.get("pattern", "")
                replacement = patch.get("replacement", "")

                if not pattern:
                    raise ValueError("regex_replace patch requires 'pattern' parameter")

                new_content, count = self.apply_regex_replace(
                    content, pattern, replacement
                )

            elif patch_type == "line_insert":
                insert_after = patch.get("insert_after", "")
                line = patch.get("line", "")

                new_content, count = self.apply_line_insert(
                    content, insert_after, line
                )

            else:
                raise ValueError(f"Unknown patch type: {patch_type}")

            result["success"] = True
            result["changes_count"] = count
            result["changes_made"] = count > 0

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            # Return original content on error
            return content, result

        return new_content, result

    def apply_patches_to_file(
        self, file_path: Path, patch_data: Dict[str, Any], json_output: Path = None
    ) -> Dict[str, Any]:
        """
        Apply all patches from YAML to a file

        Args:
            file_path: Path to file to patch
            patch_data: Loaded patch YAML data
            json_output: Optional path to write JSON report

        Returns:
            Report dictionary
        """
        # Reset per-file state
        self.patch_results = []
        self.total_changes = 0

        report = {
            "success": False,
            "file": str(file_path),
            "patch_file": Path.cwd().name,
            "patches_applied": 0,
            "total_changes": 0,
            "patches": [],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Read file content
            try:
                content = file_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                report["error"] = f"File not found: {file_path}"
                report["error_type"] = "general_error"
                report["exit_code"] = 1
                return report

            # Apply patches
            current_content = content
            patches = patch_data.get("patches", [])

            for i, patch in enumerate(patches):
                new_content, patch_result = self.apply_patch(current_content, patch)

                # If patch failed and it's not a "no changes" situation, abort
                if not patch_result["success"]:
                    report["error"] = patch_result.get("error", "Unknown error")
                    report["error_type"] = "patch_error"
                    report["exit_code"] = 3
                    report["patch_index"] = i
                    report["patch_type"] = patch_result.get("type", "unknown")
                    return report

                # Track changes
                self.patch_results.append(patch_result)
                if patch_result["changes_made"]:
                    self.total_changes += patch_result["changes_count"]

                current_content = new_content

            # Check if any changes were made
            if self.total_changes == 0:
                if self.error_no_changes:
                    report["success"] = False
                    report["error"] = "Patch did not apply any changes"
                    report["error_type"] = "no_changes"
                    report["exit_code"] = 2
                    report["changes_made"] = False
                    report["total_changes"] = 0
                    return report
                else:
                    # No error mode - just report success with 0 changes
                    report["success"] = True
                    report["exit_code"] = 0
                    report["changes_made"] = False
                    report["total_changes"] = 0
                    report["patches"] = self.patch_results
                    return report

            # Changes were made
            if not self.dry_run:
                # Create backup
                try:
                    backup_path = self.create_backup(file_path, self.backup_id)
                    report["backup_created"] = str(backup_path)
                except Exception as e:
                    report["error"] = f"Failed to create backup: {e}"
                    report["error_type"] = "filesystem_error"
                    report["exit_code"] = 4
                    return report

                # Write patched content
                try:
                    file_path.write_text(current_content, encoding="utf-8")
                except Exception as e:
                    report["error"] = f"Failed to write file: {e}"
                    report["error_type"] = "filesystem_error"
                    report["exit_code"] = 4
                    return report
            else:
                report["dry_run"] = True

            # Success
            report["success"] = True
            report["exit_code"] = 0
            report["changes_made"] = True
            report["total_changes"] = self.total_changes
            report["patches"] = self.patch_results
            report["patches_applied"] = len(patches)

        except Exception as e:
            report["error"] = str(e)
            report["error_type"] = "general_error"
            report["exit_code"] = 1

        return report

    def apply_patches_to_directory(
        self,
        directory: Path,
        patch_data: Dict[str, Any],
        recursive: bool = False,
        extensions: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply patches to all files in a directory

        Uses two-pass approach:
        1. Count matches across all files, verify aggregate counts
        2. If counts match, apply patches to each file

        Args:
            directory: Directory to process
            patch_data: Loaded patch YAML data
            recursive: If True, process subdirectories recursively
            extensions: Optional list of file extensions to include

        Returns:
            Aggregated report dictionary
        """
        files = self.collect_files(directory, recursive, extensions)

        if not files:
            return {
                "success": False,
                "mode": "directory",
                "directory": str(directory),
                "error": "No files found in directory",
                "error_type": "general_error",
                "exit_code": 1,
                "total_files": 0,
                "timestamp": datetime.now().isoformat(),
            }

        patches = patch_data.get("patches", [])

        # Phase 1: count matches per patch across all files
        aggregate_counts = [0] * len(patches)
        file_contents = {}

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                file_contents[file_path] = content
            except Exception:
                continue

            for i, patch in enumerate(patches):
                aggregate_counts[i] += self._count_matches(content, patch)

        # Phase 2: verify aggregate counts
        count_errors = []
        for i, patch in enumerate(patches):
            expected = patch.get("count")
            if expected is not None and aggregate_counts[i] != expected:
                desc = patch.get("description", f"patch {i}")
                count_errors.append(
                    f"{desc}: expected {expected}, found {aggregate_counts[i]}"
                )

        if count_errors:
            return {
                "success": False,
                "mode": "directory",
                "directory": str(directory),
                "error": "Count mismatch: " + "; ".join(count_errors),
                "error_type": "count_mismatch",
                "exit_code": 3,
                "total_files": len(files),
                "aggregate_counts": aggregate_counts,
                "timestamp": datetime.now().isoformat(),
            }

        # Phase 3: apply patches to each file
        file_reports = []
        total_changes = 0
        successful = 0
        failed = 0
        worst_exit_code = 0

        for file_path in files:
            file_report = self.apply_patches_to_file(file_path, patch_data)
            file_reports.append(file_report)
            total_changes += file_report.get("total_changes", 0)

            if file_report["success"]:
                successful += 1
            else:
                failed += 1

            exit_code = file_report.get("exit_code", 1)
            worst_exit_code = max(worst_exit_code, exit_code)

        return {
            "success": failed == 0,
            "mode": "directory",
            "directory": str(directory),
            "recursive": recursive,
            "total_files": len(files),
            "successful_files": successful,
            "failed_files": failed,
            "total_changes": total_changes,
            "aggregate_counts": aggregate_counts,
            "files": file_reports,
            "exit_code": worst_exit_code,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Apply YAML-based patches to source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="File or directory to patch (or rollback target)")
    parser.add_argument(
        "patch_file",
        nargs="?",
        help="YAML patch file (not required with --rollback)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying files",
    )
    parser.add_argument(
        "--error-no-changes",
        action="store_true",
        help="Return exit code 2 if patch makes no changes (useful for CI/CD)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively (only when targeting a directory)",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        help="Only process files with these extensions in directory mode (e.g. .cpp .h)",
    )
    parser.add_argument(
        "--json-output",
        nargs="?",
        const=None,
        help="Write JSON report to file (if no filename specified, writes to STDOUT only)",
    )
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="",
        help="Rollback mode: restore files from backups. Optional value = backup ID to target specific backups",
    )
    parser.add_argument(
        "--backup",
        help="Tag backups with an ID for targeted rollback",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete backup files after restoring (only with --rollback)",
    )

    args = parser.parse_args()

    # Resolve paths
    file_path = Path(args.file).resolve()
    patch_path = Path(args.patch_file).resolve() if args.patch_file else None
    json_output_path = Path(args.json_output) if args.json_output else None
    extensions = args.extensions if args.extensions else None

    # Create applier
    applier = PatchApplier(
        dry_run=args.dry_run,
        error_no_changes=args.error_no_changes,
        backup_id=args.backup,
    )

    # Rollback mode (--rollback or --rollback <id>)
    if args.rollback is not None:
        rollback_id = args.rollback if args.rollback else None
        report = applier.rollback(
            file_path,
            recursive=args.recursive,
            cleanup=args.cleanup,
            rollback_id=rollback_id,
        )
    else:
        if not args.patch_file:
            parser.error("patch_file is required when not using --rollback")
        try:
            # Load patch
            patch_data = applier.load_patch_yaml(patch_path)
        except Exception as e:
            report = {
                "success": False,
                "error": str(e),
                "error_type": "general_error",
                "exit_code": 1,
                "file": str(file_path),
                "patch_file": patch_path.name,
                "timestamp": datetime.now().isoformat(),
            }
            json.dump(report, sys.stdout, indent=2)
            print()
            sys.exit(1)

        # Apply patches
        if file_path.is_dir():
            report = applier.apply_patches_to_directory(
                file_path, patch_data, recursive=args.recursive, extensions=extensions
            )
        else:
            # Validate counts before applying
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                report = {
                    "success": False,
                    "error": str(e),
                    "error_type": "general_error",
                    "exit_code": 1,
                    "file": str(file_path),
                    "timestamp": datetime.now().isoformat(),
                }
                json.dump(report, sys.stdout, indent=2)
                print()
                sys.exit(1)

            count_error = applier.validate_counts_for_content(
                content, patch_data.get("patches", [])
            )
            if count_error:
                report = {
                    "success": False,
                    "error": count_error,
                    "error_type": "count_mismatch",
                    "exit_code": 3,
                    "file": str(file_path),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                report = applier.apply_patches_to_file(file_path, patch_data, json_output_path)

    # Output JSON to STDOUT (always)
    json.dump(report, sys.stdout, indent=2)
    print()

    # Write to file if specified
    if json_output_path:
        try:
            json_output_path.write_text(json.dumps(report, indent=2))
        except Exception as e:
            print(f"Warning: Failed to write JSON output file: {e}", file=sys.stderr)

    # Exit with appropriate code
    sys.exit(report.get("exit_code", 1))


if __name__ == "__main__":
    main()
