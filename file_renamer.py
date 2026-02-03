#!/usr/bin/env python3
"""
File Renamer - Batch rename files recursively with various patterns.

Features:
- Add prefix/suffix
- Search and replace patterns
- Sequential or append numbering
- Date-based renaming (modified, created, current)
- Dry-run mode for safety
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def print_progress(current: int, total: int, message: str = "Processing"):
    """Print progress on a single line that updates in place."""
    percent = (current / total * 100) if total > 0 else 0
    bar_length = 30
    filled = int(bar_length * current // total) if total > 0 else 0
    bar = "=" * filled + "-" * (bar_length - filled)
    sys.stdout.write(f"\r{message}: [{bar}] {current}/{total} ({percent:.0f}%)")
    sys.stdout.flush()


def clear_progress():
    """Clear the progress line."""
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()


def get_file_date(file_path: Path, date_type: str) -> str:
    """Get formatted date string based on date type."""
    if date_type == "modified":
        timestamp = file_path.stat().st_mtime
    elif date_type == "created":
        stat_info = file_path.stat()
        # On macOS, use st_birthtime for actual creation time
        # On Windows, st_ctime is creation time
        # On Linux, st_ctime is inode change time (no true creation time available)
        if hasattr(stat_info, 'st_birthtime'):
            timestamp = stat_info.st_birthtime  # macOS
        else:
            timestamp = stat_info.st_ctime  # Windows/Linux
    else:  # current
        timestamp = datetime.now().timestamp()

    return datetime.fromtimestamp(timestamp).strftime("%Y%m%d")


def generate_new_name(
    file_path: Path,
    prefix: str = "",
    suffix: str = "",
    search: str = None,
    replace: str = None,
    number: int = None,
    number_mode: str = "sequential",
    number_padding: int = 3,
    date_type: str = None,
    date_position: str = "prefix"
) -> str:
    """Generate new filename based on provided options."""
    stem = file_path.stem  # filename without extension
    ext = file_path.suffix  # extension including dot

    # Apply search and replace first
    if search is not None and replace is not None:
        stem = re.sub(search, replace, stem)

    # Apply prefix
    if prefix:
        stem = prefix + stem

    # Apply suffix
    if suffix:
        stem = stem + suffix

    # Apply numbering
    if number is not None:
        num_str = str(number).zfill(number_padding)
        if number_mode == "sequential":
            stem = num_str
        else:  # append
            stem = f"{stem}_{num_str}"

    # Apply date
    if date_type:
        date_str = get_file_date(file_path, date_type)
        if date_position == "prefix":
            stem = f"{date_str}_{stem}"
        else:  # suffix
            stem = f"{stem}_{date_str}"

    return stem + ext


def collect_files(root_path: Path, pattern: str = "*", recursive: bool = True) -> list:
    """Collect all files matching the pattern."""
    print("Scanning for files...", end="", flush=True)

    if recursive:
        files = list(root_path.rglob(pattern))
    else:
        files = list(root_path.glob(pattern))

    # Filter to only files (not directories)
    result = sorted([f for f in files if f.is_file()])
    print(f" found {len(result)} file(s)")
    return result


def rename_files(
    root_path: Path,
    prefix: str = "",
    suffix: str = "",
    search: str = None,
    replace: str = None,
    numbering: bool = False,
    number_mode: str = "sequential",
    number_start: int = 1,
    number_padding: int = 3,
    date_type: str = None,
    date_position: str = "prefix",
    file_pattern: str = "*",
    recursive: bool = True,
    execute: bool = False
) -> list:
    """
    Rename files based on provided options.
    Returns list of (old_path, new_path) tuples.
    """
    files = collect_files(root_path, file_pattern, recursive)
    total_files = len(files)
    renames = []
    counter = number_start
    warnings = []

    for i, file_path in enumerate(files, 1):
        print_progress(i, total_files, "Processing")

        number = counter if numbering else None

        new_name = generate_new_name(
            file_path,
            prefix=prefix,
            suffix=suffix,
            search=search,
            replace=replace,
            number=number,
            number_mode=number_mode,
            number_padding=number_padding,
            date_type=date_type,
            date_position=date_position
        )

        new_path = file_path.parent / new_name

        # Only include if name actually changes
        if new_path != file_path:
            renames.append((file_path, new_path))

            if execute:
                # Check for conflicts
                if new_path.exists() and new_path != file_path:
                    warnings.append(f"Skipping {file_path.name} - target exists: {new_name}")
                    continue
                file_path.rename(new_path)

        if numbering:
            counter += 1

    clear_progress()

    # Print any warnings that occurred
    for warning in warnings:
        print(f"WARNING: {warning}")

    return renames


def main():
    parser = argparse.ArgumentParser(
        description="Batch rename files recursively with various patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s C:\\Photos --prefix "vacation_"
  %(prog)s C:\\Documents --search "draft" --replace "final"
  %(prog)s C:\\Images --number --number-mode sequential
  %(prog)s C:\\Files --date modified --date-position prefix
  %(prog)s C:\\Data --prefix "backup_" --number --execute

Combine multiple options:
  %(prog)s C:\\Photos --prefix "2024_" --suffix "_edited" --number --execute
        """
    )

    # Required argument
    parser.add_argument(
        "path",
        type=str,
        help="Root directory path to process"
    )

    # Prefix/Suffix options
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Add prefix to filenames"
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Add suffix to filenames (before extension)"
    )

    # Search and replace
    parser.add_argument(
        "--search",
        type=str,
        help="Search pattern (supports regex)"
    )
    parser.add_argument(
        "--replace",
        type=str,
        help="Replacement string (use with --search)"
    )

    # Numbering options
    parser.add_argument(
        "--number",
        action="store_true",
        help="Enable numbering"
    )
    parser.add_argument(
        "--number-mode",
        choices=["sequential", "append"],
        default="append",
        help="Numbering mode: 'sequential' replaces name with number, 'append' adds number to end (default: append)"
    )
    parser.add_argument(
        "--number-start",
        type=int,
        default=1,
        help="Starting number (default: 1)"
    )
    parser.add_argument(
        "--number-padding",
        type=int,
        default=3,
        help="Number padding with zeros (default: 3, e.g., 001)"
    )

    # Date options
    parser.add_argument(
        "--date",
        choices=["modified", "created", "current"],
        help="Add date to filename"
    )
    parser.add_argument(
        "--date-position",
        choices=["prefix", "suffix"],
        default="prefix",
        help="Where to add date (default: prefix)"
    )

    # File filtering
    parser.add_argument(
        "--pattern",
        type=str,
        default="*",
        help="File pattern to match (default: * for all files). Example: *.jpg"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't process subdirectories"
    )

    # Execution control
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the rename (default is dry-run)"
    )

    args = parser.parse_args()

    # Validate path
    root_path = Path(args.path)
    if not root_path.exists():
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)
    if not root_path.is_dir():
        print(f"Error: Path is not a directory: {args.path}")
        sys.exit(1)

    # Validate search/replace pair
    if (args.search is None) != (args.replace is None):
        print("Error: --search and --replace must be used together")
        sys.exit(1)

    # Check if any rename option is specified
    if not any([args.prefix, args.suffix, args.search, args.number, args.date]):
        print("Error: No rename options specified. Use --prefix, --suffix, --search/--replace, --number, or --date")
        sys.exit(1)

    # Perform rename
    renames = rename_files(
        root_path=root_path,
        prefix=args.prefix,
        suffix=args.suffix,
        search=args.search,
        replace=args.replace,
        numbering=args.number,
        number_mode=args.number_mode,
        number_start=args.number_start,
        number_padding=args.number_padding,
        date_type=args.date,
        date_position=args.date_position,
        file_pattern=args.pattern,
        recursive=not args.no_recursive,
        execute=args.execute
    )

    # Output results
    if not renames:
        print("No files to rename.")
        return

    mode = "RENAMED" if args.execute else "PREVIEW (use --execute to apply)"
    print(f"\n{mode}")
    print("=" * 60)

    for old_path, new_path in renames:
        # Show relative paths for cleaner output
        try:
            old_rel = old_path.relative_to(root_path)
            new_name = new_path.name
        except ValueError:
            old_rel = old_path
            new_name = new_path.name

        print(f"{old_rel}")
        print(f"  -> {new_name}")
        print()

    print(f"Total: {len(renames)} file(s)")

    if not args.execute:
        print("\nThis was a dry-run. Add --execute to perform the actual rename.")


if __name__ == "__main__":
    main()
