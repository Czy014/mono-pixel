"""Text rendering module for pixel-style output."""

from enum import StrEnum

from PIL import Image, ImageDraw, ImageFont

from .font_loader import calculate_text_bbox, calculate_text_size, load_font


class HorizontalAlign(StrEnum):
    """Horizontal alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(StrEnum):
    """Vertical alignment options."""

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


def create_canvas(
    width: int, height: int, bg_color: str | tuple[int, int, int] = "white"
) -> Image.Image:
    """Create a canvas with given width/height and background color.

    Args:
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        bg_color: Background color.

    Returns:
        Pillow image object.

    Raises:
        ValueError: Canvas size is invalid.
    """
    if not isinstance(width, int) or width <= 0:
        raise ValueError(f"Canvas width must be a positive integer, got: {width}")
    if not isinstance(height, int) or height <= 0:
        raise ValueError(f"Canvas height must be a positive integer, got: {height}")

    return Image.new("RGB", (width, height), bg_color)


def calculate_text_position(
    text: str,
    font: ImageFont.FreeTypeFont,
    canvas_width: int,
    canvas_height: int,
    padding: int | tuple[int, int, int, int] = 0,
    align: HorizontalAlign = HorizontalAlign.CENTER,
    valign: VerticalAlign = VerticalAlign.MIDDLE,
) -> tuple[int, int]:
    """Calculate text position based on alignment and padding.

    Args:
        text: Text content.
        font: Pillow font object.
        canvas_width: Canvas width.
        canvas_height: Canvas height.
        padding: Integer or (top, right, bottom, left).
        align: Horizontal alignment.
        valign: Vertical alignment.

    Returns:
        (x, y) draw position.
    """
    if isinstance(padding, int):
        pad_top = pad_right = pad_bottom = pad_left = padding
    else:
        pad_top, pad_right, pad_bottom, pad_left = padding

    available_width = canvas_width - pad_left - pad_right
    available_height = canvas_height - pad_top - pad_bottom

    bbox = calculate_text_bbox(text, font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if align == HorizontalAlign.LEFT:
        x = pad_left - bbox[0]
    elif align == HorizontalAlign.RIGHT:
        x = canvas_width - pad_right - bbox[2]
    else:
        x = pad_left + (available_width - text_width) // 2 - bbox[0]

    if valign == VerticalAlign.TOP:
        y = pad_top - bbox[1]
    elif valign == VerticalAlign.BOTTOM:
        y = canvas_height - pad_bottom - bbox[3]
    else:
        y = pad_top + (available_height - text_height) // 2 - bbox[1]

    return (x, y)


def calculate_auto_font_size(
    text: str,
    font_path: str,
    canvas_width: int,
    canvas_height: int,
    padding: int | tuple[int, int, int, int] = 0,
    min_font_size: int = 8,
    max_font_size: int = 1024,
) -> int:
    """Auto-calculate the largest font size that fits the canvas.

    Args:
        text: Text content.
        font_path: Font file path.
        canvas_width: Canvas width.
        canvas_height: Canvas height.
        padding: Padding configuration.
        min_font_size: Minimum font size.
        max_font_size: Maximum font size.

    Returns:
        Best fitting font size.
    """
    if isinstance(padding, int):
        pad_top = pad_right = pad_bottom = pad_left = padding
    else:
        pad_top, pad_right, pad_bottom, pad_left = padding

    available_width = canvas_width - pad_left - pad_right
    available_height = canvas_height - pad_top - pad_bottom

    # Binary search for best-fit size.
    low = min_font_size
    high = max_font_size
    best_size = min_font_size

    while low <= high:
        mid = (low + high) // 2

        try:
            font = load_font(font_path, mid)
            text_width, text_height = calculate_text_size(text, font)

            if text_width <= available_width and text_height <= available_height:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        except Exception:
            high = mid - 1

    return best_size


def render_pixel_text(
    canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    position: tuple[int, int],
    fg_color: str | tuple[int, int, int] = "black",
) -> Image.Image:
    """Render text to canvas in pixel style.

    Args:
        canvas: Canvas image.
        text: Text content.
        font: Pillow font object.
        position: Draw position.
        fg_color: Foreground text color.

    Returns:
        Rendered image.
    """
    draw = ImageDraw.Draw(canvas)

    draw.text(
        position,
        text,
        font=font,
        fill=fg_color,
    )

    return canvas


def render_text(
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
) -> Image.Image:
    """Run the full text rendering pipeline.

    Args:
        text: Text content.
        font_path: Font file path.
        image_size: Output size as (width, height).
        font_size: Manual font size.
        auto_fit: Whether to auto-fit font size.
        padding: Padding configuration.
        align: Horizontal alignment.
        valign: Vertical alignment.
        bg_color: Background color.
        fg_color: Foreground color.

    Returns:
        Rendered image.

    Raises:
        ValueError: Invalid parameters.
    """
    if not text:
        raise ValueError("Text cannot be empty")

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        raise ValueError("Specify exactly one of font_size or auto_fit")

    if isinstance(align, str):
        align = HorizontalAlign(align)
    if isinstance(valign, str):
        valign = VerticalAlign(valign)

    canvas = create_canvas(image_size[0], image_size[1], bg_color)

    if auto_fit:
        calculated_font_size = calculate_auto_font_size(
            text, font_path, image_size[0], image_size[1], padding
        )
        if calculated_font_size is None:
            raise ValueError("Could not auto-calculate font size")
        font_size = calculated_font_size

    if font_size is None:
        raise ValueError("Font size is required unless auto_fit is enabled")

    font = load_font(font_path, font_size)

    position = calculate_text_position(
        text, font, image_size[0], image_size[1], padding, align, valign
    )

    canvas = render_pixel_text(canvas, text, font, position, fg_color)

    return canvas
