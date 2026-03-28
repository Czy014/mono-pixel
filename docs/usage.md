# Usage

This document describes how to install, run, and use `mono-pixel` from both the CLI
and the Python API.

## Installation

Install dependencies from the project root (this project uses a `pyproject.toml`):

```bash
python -m pip install -e .
# or use the project's development workflow, e.g. `uv run` commands included in the repo
```

Required runtime dependencies:
- Pillow
- Typer (for the CLI)

## CLI Quickstart

To see available commands:

```bash
uv run mono-pixel --help
```

Basic example: render text to an image file

```bash
uv run mono-pixel run \
  --text "Hello World" \
  --font-path /path/to/font.ttf \
  --image-size 512 256 \
  --font-size 64 \
  --output out.png
```

Preview ASCII in terminal:

```bash
uv run mono-pixel run --text "Preview" --font-path /path/to/font.ttf --preview-ascii
```

See `uv run mono-pixel run --help` for all CLI options (padding, align, colors, binarization, etc.).
