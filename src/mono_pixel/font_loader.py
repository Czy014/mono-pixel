"""Font loading and validation utilities."""

from importlib import resources
from pathlib import Path

from PIL import ImageFont

from .utils.exceptions import (
    FontError,
    FontNotFoundError,
    InvalidFontError,
    ResourceAccessError,
)

# Re-export exceptions for backward compatibility
__all__ = [
    "FontError",
    "FontNotFoundError",
    "InvalidFontError",
    "validate_font_file",
    "load_font",
    "get_font_metrics",
    "calculate_text_bbox",
    "calculate_text_size",
    "get_builtin_fonts",
    "get_bundled_font_path",
    "load_builtin_font",
]


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


def get_builtin_fonts() -> list[str]:
    """Get list of available bundled fonts.

    Returns:
        List of font filenames.

    Raises:
        ResourceAccessError: If the fonts directory cannot be accessed.
    """
    font_names = []
    try:
        font_dir = resources.files("mono_pixel.fonts")
        for item in font_dir.iterdir():
            if item.is_file():
                name = item.name
                if name.lower().endswith((".ttf", ".otf", ".ttc", ".otc")):
                    font_names.append(name)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise ResourceAccessError("Failed to access bundled fonts directory") from e
    except Exception as e:
        raise ResourceAccessError(
            f"Unexpected error while accessing bundled fonts: {e}"
        ) from e
    return sorted(font_names)


def get_bundled_font_path(font_name: str) -> Path:
    """Get path to a bundled font file.

    Args:
        font_name: Name of the bundled font file.

    Returns:
        Path to the font file.

    Raises:
        FontNotFoundError: If the bundled font does not exist.
        ResourceAccessError: If the font resource cannot be accessed.
    """
    # First check if the font exists in our list
    try:
        available_fonts = get_builtin_fonts()
    except ResourceAccessError as e:
        raise ResourceAccessError(f"Cannot verify font availability: {e}") from e

    if font_name not in available_fonts:
        raise FontNotFoundError(f"Bundled font not found: {font_name}")

    try:
        # Get the actual path
        with resources.path("mono_pixel.fonts", font_name) as font_path:
            return Path(font_path)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise ResourceAccessError(f"Failed to access font resource: {font_name}") from e
    except Exception as e:
        raise ResourceAccessError(
            f"Unexpected error accessing font {font_name}: {e}"
        ) from e


def load_builtin_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
    """Load a bundled font with a given size.

    Args:
        font_name: Name of the bundled font file.
        font_size: Font size in pixels.

    Returns:
        Pillow FreeType font object.

    Raises:
        FontNotFoundError: Bundled font does not exist.
        InvalidFontError: Bundled font is invalid.
        ValueError: Font size is invalid.
    """
    font_path = get_bundled_font_path(font_name)
    return load_font(font_path, font_size)
