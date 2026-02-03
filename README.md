# File Renamer

A command-line tool for batch renaming files recursively with various patterns.

## Features

- **Prefix/Suffix**: Add text before or after filenames
- **Search & Replace**: Find and replace text in filenames (supports regex)
- **Numbering**: Sequential numbering or append numbers to existing names
- **Date-based**: Add file modified date, created date, or current date
- **Combine options**: Use multiple features together in a single operation
- **Dry-run mode**: Preview changes before applying them

## Prerequisites

### Installing Python

**Windows:**

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check the box "Add Python to PATH" during installation
4. Click "Install Now"

To verify the installation, open Command Prompt and run:

```bash
python --version
```

You should see something like `Python 3.12.x`.

**macOS:**

Python 3 may already be installed. Check by running:

```bash
python3 --version
```

If not installed, you can install it via:
- [Homebrew](https://brew.sh/): `brew install python`
- Or download from [python.org](https://www.python.org/downloads/)

On macOS, use `python3` instead of `python` to run the script:

```bash
python3 file_renamer.py /path/to/folder --prefix "test_"
```

### Dependencies

This script uses only Python standard library modules. No additional packages are required.

## Usage

```bash
# Windows
python file_renamer.py <path> [options]

# macOS/Linux
python3 file_renamer.py <path> [options]
```

By default, the script runs in **dry-run mode** and shows a preview of changes. Add `--execute` to perform the actual rename.

**Note:** Examples below use Windows-style paths (`C:\Photos`). On macOS/Linux, use Unix-style paths (`/Users/name/Photos` or `~/Photos`).

## Examples

### Add Prefix or Suffix

```bash
# Add prefix to all files
python file_renamer.py C:\Photos --prefix "vacation_"

# Add suffix to all files
python file_renamer.py C:\Documents --suffix "_backup"
```

### Search and Replace

```bash
# Replace text in filenames (supports regex)
python file_renamer.py C:\Files --search "draft" --replace "final"

# Using regex: remove numbers from filenames
python file_renamer.py C:\Files --search "\d+" --replace ""
```

### Numbering

```bash
# Sequential numbering (replaces entire name)
# photo.jpg -> 001.jpg
python file_renamer.py C:\Images --number --number-mode sequential

# Append numbering (preserves name)
# photo.jpg -> photo_001.jpg
python file_renamer.py C:\Images --number --number-mode append

# Custom start number and padding
python file_renamer.py C:\Images --number --number-start 100 --number-padding 4
```

### Date-Based Renaming

```bash
# Add file modified date as prefix
# photo.jpg -> 20240115_photo.jpg
python file_renamer.py C:\Files --date modified --date-position prefix

# Add creation date as suffix
# photo.jpg -> photo_20240115.jpg
python file_renamer.py C:\Files --date created --date-position suffix

# Use current date
python file_renamer.py C:\Files --date current
```

**Platform note:** The `--date created` option uses the actual file creation time on Windows and macOS. On Linux, true creation time is not available, so it falls back to inode change time.

### Combining Options

```bash
# Add prefix, suffix, and numbering together
python file_renamer.py C:\Photos --prefix "2024_" --suffix "_edited" --number --execute

# Date prefix with search/replace
python file_renamer.py C:\Documents --date modified --search "draft" --replace "final" --execute
```

### Filtering Files

```bash
# Only process .jpg files
python file_renamer.py C:\Photos --pattern "*.jpg" --prefix "photo_"

# Only process current directory (no subdirectories)
python file_renamer.py C:\Documents --no-recursive --prefix "doc_"
```

## Options Reference

| Option | Description |
|--------|-------------|
| `path` | Root directory to process (required) |
| `--prefix TEXT` | Add prefix to filenames |
| `--suffix TEXT` | Add suffix to filenames (before extension) |
| `--search PATTERN` | Search pattern (supports regex) |
| `--replace TEXT` | Replacement string (use with --search) |
| `--number` | Enable numbering |
| `--number-mode MODE` | `sequential` (replace name) or `append` (add to name) |
| `--number-start N` | Starting number (default: 1) |
| `--number-padding N` | Zero-padding width (default: 3) |
| `--date TYPE` | Add date: `modified`, `created`, or `current` |
| `--date-position POS` | Date placement: `prefix` or `suffix` |
| `--pattern GLOB` | File pattern to match (default: `*` for all) |
| `--no-recursive` | Don't process subdirectories |
| `--execute` | Actually perform the rename (default is dry-run) |

## Progress Indicator

The script displays a progress bar while processing files:

```
Scanning for files... found 150 file(s)
Processing: [==================------------] 92/150 (61%)
```

## Safety

- **Dry-run by default**: The script shows what would be renamed without making changes
- **Conflict detection**: Skips files if the target name already exists
- **Preview output**: Review all changes before adding `--execute`

## License

MIT License - Free to use and modify.
