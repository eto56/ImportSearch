# importsearch

importsearch is a CLI tool that inspects Python files and reports the import dependency graph for a given entry point.  
Specify a target file and instantly view the downstream files and modules that it touches.

> Looking for the Japanese guide? See [README-ja.md](./README-ja.md).

## Features

- **Rich CLI report:** Presents dependencies and visited files in a styled table.
- **Multiple output formats:** Choose between `print` (decorated), `text`, and `json`.
- **Stable traversal:** Works on `Path` objects, avoiding cycles and duplicates during analysis.

## Installation

```bash
pip install importsearch
```

## CLI Usage

```bash
importsearch path/to/main.py --root . --output-format print
```

### Common options

- `--root / -r`: Root directory for the analysis (defaults to the current directory)  
- `--output-format / -o`: `print` | `text` | `json`  
- `--output-file / -of`: Base name for `text` / `json` reports (extension is added automatically)  
- `--verbose / -v`: Display progress logs during the walk

### Example: Save a text report

```bash
importsearch src/main.py --root . --output-format text --output-file report
```

The command prints the summary to stdout and writes it to `report.txt`.

## Optional: Programmatic Usage

While the CLI is the primary interface, you can instantiate the searcher directly:

```python
import argparse
from pathlib import Path
from importsearch import importsearch

args = argparse.Namespace(
    file_path=Path("src/main.py"),
    root_path=Path("."),
    output_format="json",
    output_path=Path("dependencies"),
    verbose=False,
)

searcher = importsearch(args)
searcher.search()
searcher.summary()
```

## Development

Run the test suite with `pytest`:

```bash
pytest
```

Contributions are welcome! If you have ideas for improvements, please open an issue or submit a pull request.
