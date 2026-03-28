# mono-pixel

![mono-pixel logo](docs/mono-pixel-logo.png)

mono-pixel is a small Python library and CLI for rendering high-contrast, "pixel"-style text
images suitable for LED-like displays, e-paper, or retro-styled graphics. It provides utilities
for loading fonts, calculating text layout, rendering text to an image, and exporting images
with strict binarization.

Features
- Render text into fixed-size pixel canvases
- Automatic font sizing to fit text into a target box
- Strict binarization and monochrome export
- Small, dependency-light implementation (Pillow + Typer)

Quick start
1. See the detailed usage guide in the `docs` directory: [Usage](docs/usage.md)
2. From source you can run the CLI with:

```
uv run mono-pixel --help
```

License
This project is available under the terms described in the `LICENSE.txt` file.

