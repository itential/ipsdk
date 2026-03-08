#!/usr/bin/env python3
# Copyright (C) Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


"""Check that all Python files have proper license headers.

This script verifies that all .py files in src/ipsdk, tests, and scripts
directories contain the required copyright, license, and SPDX identifier headers.

Required headers:
    # Copyright (C) Itential, Inc
    # GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
    # SPDX-License-Identifier: GPL-3.0-or-later

Usage:
    python scripts/check_license_headers.py         # Check only
    python scripts/check_license_headers.py --fix   # Fix missing headers

Exit codes:
    0 - All files have proper headers (or were fixed)
    1 - One or more files are missing proper headers (check mode only)
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path


REQUIRED_HEADERS = [
    "# Copyright (C) Itential, Inc",
    "# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)",
    "# SPDX-License-Identifier: GPL-3.0-or-later",
]

_HEADER_PREFIXES = (
    "# Copyright",
    "# GNU General Public License",
    "# SPDX-License-Identifier",
)


def check_file_header(file_path: Path) -> bool:
    """Check if a file has the required license headers.

    Args:
        file_path: Path to the Python file to check

    Returns:
        True if the file has proper headers, False otherwise
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = {line.rstrip() for line in itertools.islice(f, 10)}
    except OSError as e:
        print(f"Error reading {file_path}: {e}")
        return False

    return all(header in lines for header in REQUIRED_HEADERS)


def fix_file_header(file_path: Path) -> bool:
    """Add the required license headers to a file.

    This function intelligently handles files that may already have partial headers
    by removing any existing header lines and replacing them with the complete set.

    Args:
        file_path: Path to the Python file to fix

    Returns:
        True if the file was fixed successfully, False otherwise
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"Error reading {file_path}: {e}")
        return False

    lines = content.splitlines(keepends=True)

    # Check if file starts with shebang
    shebang_lines = []
    start_position = 0
    if lines and lines[0].startswith("#!"):
        shebang_lines = [lines[0]]
        start_position = 1

    # Remove any existing partial headers
    # Look for lines that match any part of our required headers
    content_start = start_position
    for i in range(start_position, min(start_position + 10, len(lines))):
        line = lines[i].rstrip()
        is_header_line = line.startswith(_HEADER_PREFIXES)

        if is_header_line:
            content_start = i + 1
        elif not line or not line.startswith("#"):
            # Empty line or non-comment line signals end of header block
            content_start = i
            break

    # Build the header to insert
    header_lines = [f"{header}\n" for header in REQUIRED_HEADERS]
    header_lines.append("\n")  # Add blank line after headers

    # Build the new file content
    new_lines = shebang_lines + header_lines + lines[content_start:]

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except OSError as e:
        print(f"Error writing {file_path}: {e}")
        return False


def find_python_files(root_dir: Path) -> list[Path]:
    """Find all Python files in a directory recursively.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Path objects for all .py files found
    """
    return sorted(root_dir.rglob("*.py"))


def main() -> int:
    """Main function to check license headers in all Python files.

    Returns:
        Exit code: 0 if all files pass, 1 if any file fails
    """
    parser = argparse.ArgumentParser(
        description="Check or fix license headers in Python files"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically add missing license headers",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    scan_dirs = [
        repo_root / "src" / "ipsdk",
        repo_root / "tests",
        repo_root / "scripts",
    ]

    # Find all Python files across all scanned directories
    python_files: list[Path] = sorted(
        itertools.chain.from_iterable(
            find_python_files(d) for d in scan_dirs if d.exists()
        )
    )

    if not python_files:
        print("No Python files found to check")
        return 0

    # Check each file
    files_without_headers: list[Path] = []
    for file_path in python_files:
        if not check_file_header(file_path):
            files_without_headers.append(file_path)

    # Report results
    total_files = len(python_files)
    files_with_headers = total_files - len(files_without_headers)

    print(f"Checked {total_files} Python files")
    print(f"  ✓ {files_with_headers} files have proper headers")

    if files_without_headers:
        print(f"  ✗ {len(files_without_headers)} files are missing proper headers:")
        for file_path in files_without_headers:
            rel_path = file_path.relative_to(repo_root)
            print(f"    - {rel_path}")

        if args.fix:
            print()
            print("Fixing files...")
            fixed_files: list[Path] = []
            failed_files: list[Path] = []

            for file_path in files_without_headers:
                if fix_file_header(file_path):
                    fixed_files.append(file_path)
                else:
                    failed_files.append(file_path)

            print(f"  ✓ Fixed {len(fixed_files)} files")
            if failed_files:
                print(f"  ✗ Failed to fix {len(failed_files)} files:")
                for file_path in failed_files:
                    rel_path = file_path.relative_to(repo_root)
                    print(f"    - {rel_path}")
                return 1

            print()
            print("All files now have proper license headers!")
            return 0
        else:
            print()
            print("Required headers:")
            for header in REQUIRED_HEADERS:
                print(f"  {header}")
            print()
            print("Run with --fix to automatically add missing headers")
            return 1

    print()
    print("All files have proper license headers!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
