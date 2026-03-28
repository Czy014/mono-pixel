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

### Core options

| Option | Short | Description |
|--------|-------|-------------|
| `--text` | `-t` | Text to render |
| `--text-file` | | Read text from a file (`UTF-8`) |
| `--font-path` | `-f` | Path to a `.ttf` / `.otf` font file |
| `--image-size` | `-s` | Output image size, e.g. `1024x1024` (also accepts `X`, `*`, space as separator) |
| `--font-size` | `-z` | Manual font size in **pixels** (mutually exclusive with `--auto-fit`) |
| `--auto-fit` | `-a` | Auto-fit font size to fill the canvas (mutually exclusive with `--font-size`) |
| `--output` | `-o` | Output PNG path (default: `output.png`) |

> **Note:** you must supply exactly one of `--font-size` or `--auto-fit`.

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
| `--dpi` | `72` | Output image DPI |
| `--overwrite` | | Overwrite the output file without prompting |
| `--quiet` / `-q` | | Quiet mode — suppress all progress and status messages |

### Binarization

Mono-pixel renders strictly monochrome images by default (every pixel becomes either pure black or pure white).

| Option | Default | Description |
|--------|---------|-------------|
| `--no-binarization` | | Keep the original grayscale image (disable strict binarization) |
| `--binarization-threshold` | `127` | Threshold 0–255; pixels above this become background, below become foreground |

### Interactive mode

When run with no arguments, `mono-pixel run` enters interactive mode and prompts for:
`Text source` → `Text to render` → `TTF/OTF font path` → `Image size` → `Font size mode` → `Output file path`

## Python API

```python
from mono_pixel import generate_pixel_text
from mono_pixel.renderer import HorizontalAlign, VerticalAlign
from mono_pixel.font_loader import load_font

# High-level API — auto-fits font size
image = generate_pixel_text(
    text="Hello World",
    font_path="fonts/PICO-8.ttf",
    image_size=(1024, 256),
    align=HorizontalAlign.CENTER,
    valign=VerticalAlign.MIDDLE,
    bg_color="white",
    fg_color="black",
)

# Auto font sizing
from mono_pixel.renderer import calculate_auto_font_size
size = calculate_auto_font_size(
    text="Hello",
    font_path="fonts/PICO-8.ttf",
    canvas_width=1024,
    canvas_height=256,
    padding=16,
)

# Manual rendering
from mono_pixel.renderer import render_text
image = render_text(
    text="Hello",
    font_path="fonts/PICO-8.ttf",
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
from mono_pixel.exporter import save_image
save_image(image, "out.png", strict_binarize=True, dpi=(300, 300))
```

