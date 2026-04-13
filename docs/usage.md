# Usage

## Installation

```bash
# via uvx (no clone needed)
uvx mono-pixel --help

# via pipx (isolated user install)
pipx install mono-pixel

# from source
git clone https://github.com/czy014/mono-pixel.git
cd mono-pixel
uv sync
uv run mono-pixel --help
```

## CLI

`mono-pixel run [OPTIONS]` is the main command. Run without arguments to enter interactive mode.

### Global options

| Option | Description |
|--------|-------------|
| `-V, --version` | Show version and exit |

### Commands

| Command | Description |
|---------|-------------|
| `list-fonts` | List all available built-in fonts |
| `run` | Render pixel text image (default command) |

### Core options (run command)

| Option | Short | Description |
|--------|-------|-------------|
| `--text` | `-t` | Text to render |
| `--text-file` | | Read text from a file (`UTF-8`) |
| `--font-path` | `-f` | Path to a `.ttf` / `.otf` font file |
| `--builtin-font` | `-b` | Use a built-in font (use `list-fonts` to see available options) |
| `--image-size` | `-s` | Output image size, e.g. `1024x1024` (also accepts `X`, `*`, space as separator) |
| `--font-size` | `-z` | Manual font size in **pixels** (mutually exclusive with `--auto-fit`) |
| `--auto-fit` | `-a` | Auto-fit font size to fill the canvas (mutually exclusive with `--font-size`) |
| `--output` | `-o` | Output file path (`.png` for raster, `.svg` for vector; default: `output.png`) |

> **Note:** 
> - You must supply exactly one of `--font-size` or `--auto-fit`.
> - You must supply exactly one of `--font-path` or `--builtin-font`.

### Preview

| Option | Description |
|--------|-------------|
| `--preview` / `-p` | Preview only; do not save an output file |
| `--preview-ascii` | Show raw ASCII preview (character fill, no overlays) |
| `--preview-image` | Reserved for image preview fallback |
| `--no-preview` | Skip all previews and go straight to rendering |
| `--force` | Skip layout validation, preview, and all confirmation prompts |

The default preview (when neither flag is set) shows a **position-aware ASCII preview** — the canvas is drawn with a frame, and the rendered glyphs are overlaid with a bounding box so you can see exactly where the text sits.

```
+--------------------------------------------------------------------------------+
|                                                                                |
| ***************************************************************************    |
| *@@@@@@@@@   @@@@@@@@@@      @@@@@@@      @@@@@@@                @@@@@@@@@*    |
| ...
| ***************************************************************************    |
+--------------------------------------------------------------------------------+
```

### Layout

| Option | Default | Description |
|--------|---------|-------------|
| `--padding` / `-P` | `16` | Canvas padding. Formats: `16` (all sides), `10,20` (vertical,horizontal), `10,20,30,40` (top,right,bottom,left) |
| `--align` | `center` | Horizontal alignment: `left`, `center`, `right`, `stretch` |
| `--valign` | `middle` | Vertical alignment: `top`, `middle`, `bottom` |
| `--bg-color` | `white` | Background color name |
| `--fg-color` | `black` | Foreground (text) color name |

### Output

| Option | Default | Description |
|--------|---------|-------------|
| `--dpi` | `72` | Output image DPI (for PNG) |
| `--overwrite` | | Overwrite the existing output file without prompting |
| `--quiet` / `-q` | | Quiet mode — suppress all progress and status messages |

> **Note:** Output format is determined by file extension. Use `.png` for raster images (default) or `.svg` for vector graphics.

### Binarization

Mono-pixel renders strictly monochrome images by default (every pixel becomes either pure black or pure white).

| Option | Default | Description |
|--------|---------|-------------|
| `--no-binarization` | | Keep the original grayscale image (disable strict binarization) |
| `--binarization-threshold` | `127` | Threshold 0–255; pixels above this become background, below become foreground |

### Interactive mode

When run with no arguments, `mono-pixel run` enters interactive mode and prompts for:
`Text source` → `Text to render` → `Font source (builtin or custom)` → `Image size` → `Font size mode` → `Output file path`

### List built-in fonts

Use the `list-fonts` command to see all available built-in fonts:

```bash
mono-pixel list-fonts
```

Example output:
```
Available built-in fonts:

  - pico8-mono.ttf
  - pixel32.ttf
```

### Using built-in fonts

To use a built-in font, use the `--builtin-font` option with the `run` command:

```bash
mono-pixel run --text "Hello Pixel!" --builtin-font pico8-mono.ttf --image-size 512x512 --auto-fit
```

## Python API

```python
from mono_pixel import (
    generate_pixel_text,
    get_builtin_fonts,
    get_bundled_font_path,
    load_builtin_font,
)
from mono_pixel.components.renderer import HorizontalAlign, VerticalAlign
from mono_pixel.components.font_loader import load_font

# List available built-in fonts
fonts = get_builtin_fonts()
print("Available fonts:", fonts)

# High-level API — using custom font
image = generate_pixel_text(
    text="Hello World",
    font_path="path/to/custom.ttf",
    image_size=(1024, 256),
    align=HorizontalAlign.CENTER,
    valign=VerticalAlign.MIDDLE,
    bg_color="white",
    fg_color="black",
)

# High-level API — using built-in font
image = generate_pixel_text(
    text="Hello World",
    builtin_font="pico8-mono.ttf",
    image_size=(1024, 256),
    align=HorizontalAlign.CENTER,
    valign=VerticalAlign.MIDDLE,
    bg_color="white",
    fg_color="black",
)

# Auto font sizing
from mono_pixel.components.renderer import calculate_auto_font_size

# Using custom font
size = calculate_auto_font_size(
    text="Hello",
    font_path="path/to/custom.ttf",
    canvas_width=1024,
    canvas_height=256,
    padding=16,
)

# Using built-in font
font_path = get_bundled_font_path("pixel32.ttf")
size = calculate_auto_font_size(
    text="Hello",
    font_path=str(font_path),
    canvas_width=1024,
    canvas_height=256,
    padding=16,
)

# Load built-in font directly
font = load_builtin_font("pico8-mono.ttf", 32)

# Manual rendering
from mono_pixel.components.renderer import render_text

# Using custom font
image = render_text(
    text="Hello",
    font_path="path/to/custom.ttf",
    image_size=(1024, 256),
    font_size=64,
    auto_fit=False,
    padding=16,
    align=HorizontalAlign.CENTER,
    valign=VerticalAlign.MIDDLE,
    bg_color="white",
    fg_color="black",
)

# Using built-in font
image = render_text(
    text="Hello",
    font_path=str(get_bundled_font_path("pixel32.ttf")),
    image_size=(1024, 256),
    font_size=64,
    auto_fit=False,
    padding=16,
    align=HorizontalAlign.CENTER,
    valign=VerticalAlign.MIDDLE,
    bg_color="white",
    fg_color="black",
)

# Export
from mono_pixel.components.exporter import save_image, export_to_svg

# Export to PNG (default)
save_image(image, "out.png", strict_binarize=True, dpi=(300, 300))

# Export to SVG (vector graphics)
# Automatically detects format from file extension
save_image(image, "out.svg", svg_pixel_size=2)

# Or use the dedicated SVG export function directly
export_to_svg(
    image,
    "out.svg",
    bg_color="white",
    fg_color="black",
    pixel_size=1,
)
```

