"""High-fidelity pixel text rendering engine."""

from __future__ import annotations

from PIL import Image

from .exporter import save_image, strict_binarization
from .font_loader import (
    FontError,
    FontNotFoundError,
    InvalidFontError,
    calculate_text_size,
    load_font,
    validate_font_file,
)
from .renderer import (
    HorizontalAlign,
    VerticalAlign,
    calculate_auto_font_size,
    create_canvas,
    render_pixel_text,
    render_text,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "FontError",
    "FontNotFoundError",
    "InvalidFontError",
    # Enums
    "HorizontalAlign",
    "VerticalAlign",
    # Font loader
    "validate_font_file",
    "load_font",
    "calculate_text_size",
    # Renderer
    "create_canvas",
    "calculate_auto_font_size",
    "render_pixel_text",
    "render_text",
    # Exporter
    "strict_binarization",
    "save_image",
    # High-level API
    "generate_pixel_text",
]


def generate_pixel_text(
    text: str,
    font_path: str,
    image_size: tuple[int, int],
    font_size: int | None = None,
    auto_fit: bool = False,
    padding: int | tuple[int, int, int, int] = 16,
    align: HorizontalAlign | str = HorizontalAlign.CENTER,
    valign: VerticalAlign | str = VerticalAlign.MIDDLE,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    output_path: str | None = None,
    strict_binarize: bool = True,
    binarization_threshold: int = 127,
    dpi: tuple[int, int] = (72, 72),
) -> Image.Image:
    """Generate a pixel-style text image with a single high-level API.

    Args:
        text: Text to render.
        font_path: Path to TTF/OTF font file.
        image_size: Output image size as (width, height).
        font_size: Manual font size in pixels; mutually exclusive with auto_fit.
        auto_fit: Whether to auto-fit font size.
        padding: Padding value or (top, right, bottom, left).
        align: Horizontal alignment.
        valign: Vertical alignment.
        bg_color: Background color.
        fg_color: Foreground (text) color.
        output_path: Output PNG path. If None, image is not saved.
        strict_binarize: Whether to strictly binarize output.
        binarization_threshold: Binarization threshold.
        dpi: Output DPI.

    Returns:
        Rendered PIL image object.

    Raises:
        ValueError: Invalid argument combination.
        FontNotFoundError: Font file does not exist.
        InvalidFontError: Font file is invalid.
    """
    if not text:
        raise ValueError("Text cannot be empty")

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        raise ValueError("Specify exactly one of font_size or auto_fit")

    image = render_text(
        text=text,
        font_path=font_path,
        image_size=image_size,
        font_size=font_size,
        auto_fit=auto_fit,
        padding=padding,
        align=align,
        valign=valign,
        bg_color=bg_color,
        fg_color=fg_color,
    )

    if output_path is not None:
        save_image(
            image=image,
            output_path=output_path,
            strict_binarize=strict_binarize,
            bg_color=bg_color,
            fg_color=fg_color,
            binarization_threshold=binarization_threshold,
            dpi=dpi,
            optimize=True,
        )

    return image
