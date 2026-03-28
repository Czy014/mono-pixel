"""Font loading and validation utilities."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont


class FontError(Exception):
    """Base class for font-related errors."""

    pass


class FontNotFoundError(FontError):
    """Raised when a font file cannot be found."""

    pass


class InvalidFontError(FontError):
    """Raised when a font file is invalid or unreadable."""

    pass


def validate_font_file(font_path: str | Path) -> Path:
    """Validate whether a font file is usable.

    Args:
        font_path: Font file path.

    Returns:
        Validated font file path.

    Raises:
        FontNotFoundError: Font file does not exist.
        InvalidFontError: Font file is invalid or unreadable.
    """
    path = Path(font_path)

    if not path.exists():
        raise FontNotFoundError(f"Font file does not exist: {font_path}")

    if not path.is_file():
        raise InvalidFontError(f"Path is not a file: {font_path}")

    supported_extensions = {".ttf", ".otf", ".ttc", ".otc"}
    if path.suffix.lower() not in supported_extensions:
        supported_extensions_text = ", ".join(sorted(supported_extensions))
        raise InvalidFontError(
            f"Unsupported font format: {path.suffix}. "
            f"Supported: {supported_extensions_text}"
        )

    file_size = path.stat().st_size
    if file_size < 1024:
        raise InvalidFontError(
            f"Font file too small (possibly corrupted): {font_path} ({file_size} bytes)"
        )

    try:
        ImageFont.truetype(str(path), 12)
    except Exception as e:
        raise InvalidFontError(
            f"Failed to load font file: {font_path}. Error: {e}"
        ) from e

    return path


def load_font(font_path: str | Path, font_size: int) -> ImageFont.FreeTypeFont:
    """Load font file with a given size.

    Args:
        font_path: Font file path.
        font_size: Font size in pixels.

    Returns:
        Pillow FreeType font object.

    Raises:
        FontNotFoundError: Font file does not exist.
        InvalidFontError: Font file is invalid.
        ValueError: Font size is invalid.
    """
    if not isinstance(font_size, int) or font_size <= 0:
        raise ValueError(f"Font size must be a positive integer, got: {font_size}")

    validated_path = validate_font_file(font_path)

    try:
        return ImageFont.truetype(str(validated_path), font_size)
    except Exception as e:
        raise InvalidFontError(
            f"Failed to load font: {validated_path}. Error: {e}"
        ) from e


def get_font_metrics(
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int, int]:
    """Get basic font metrics.

    Args:
        font: Pillow font object.

    Returns:
        (ascent, descent, line_height) tuple in pixels.
    """
    ascent, descent = font.getmetrics()
    line_height = ascent + descent

    return ascent, descent, line_height


def calculate_text_bbox(
    text: str, font: ImageFont.FreeTypeFont
) -> tuple[int, int, int, int]:
    """Compute text bounding box.

    Args:
        text: Text content.
        font: Pillow font object.

    Returns:
        Bounding box as (left, top, right, bottom).
    """
    bbox = font.getbbox(text)
    if bbox is None:
        return (0, 0, 0, 0)

    left = int(bbox[0])
    top = int(bbox[1])
    right = int(bbox[2])
    bottom = int(bbox[3])
    return (left, top, right, bottom)


def calculate_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """Compute rendered text size.

    Args:
        text: Text content.
        font: Pillow font object.

    Returns:
        (width, height) in pixels.
    """
    bbox = calculate_text_bbox(text, font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return (width, height)
