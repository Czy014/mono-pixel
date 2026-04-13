"""Font loading and validation utilities."""

from importlib import resources
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..utils.exceptions import (
    FontError,
    FontNotFoundError,
    InvalidFontError,
    ResourceAccessError,
)

__all__ = [
    "FontError",
    "FontNotFoundError",
    "InvalidFontError",
    "FontLoader",
    "validate_font_file",
    "load_font",
    "get_font_metrics",
    "calculate_text_bbox",
    "calculate_text_size",
    "get_multiline_spacing",
    "get_builtin_fonts",
    "get_bundled_font_path",
    "load_builtin_font",
]


class FontLoader:
    """Object-oriented facade for font loading and validation."""

    def get_multiline_spacing(self, font: ImageFont.FreeTypeFont) -> int:
        ascent, descent = font.getmetrics()
        nominal_size = getattr(font, "size", ascent + descent)
        return max(1, int(nominal_size * 0.18))

    def validate_font_file(self, font_path: str | Path) -> Path:
        path = Path(font_path)

        if not path.exists():
            raise FontNotFoundError(f"Font file does not exist: {font_path}")

        if not path.is_file():
            raise InvalidFontError(f"Path is not a file: {font_path}")

        supported_extensions = {".ttf", ".otf", ".ttc", ".otc"}
        if path.suffix.lower() not in supported_extensions:
            supported_extensions_text = ", ".join(sorted(supported_extensions))
            raise InvalidFontError(
                "Unsupported font format: "
                f"{path.suffix}. Supported: {supported_extensions_text}"
            )

        file_size = path.stat().st_size
        if file_size < 1024:
            raise InvalidFontError(
                "Font file too small (possibly corrupted): "
                f"{font_path} ({file_size} bytes)"
            )

        try:
            ImageFont.truetype(str(path), 12)
        except Exception as e:
            raise InvalidFontError(
                f"Failed to load font file: {font_path}. Error: {e}"
            ) from e

        return path

    def load_font(
        self, font_path: str | Path, font_size: int
    ) -> ImageFont.FreeTypeFont:
        if not isinstance(font_size, int) or font_size <= 0:
            raise ValueError(f"Font size must be a positive integer, got: {font_size}")

        validated_path = self.validate_font_file(font_path)

        try:
            return ImageFont.truetype(str(validated_path), font_size)
        except Exception as e:
            raise InvalidFontError(
                f"Failed to load font: {validated_path}. Error: {e}"
            ) from e

    def get_font_metrics(self, font: ImageFont.FreeTypeFont) -> tuple[int, int, int]:
        ascent, descent = font.getmetrics()
        return ascent, descent, ascent + descent

    def calculate_text_bbox(
        self, text: str, font: ImageFont.FreeTypeFont
    ) -> tuple[int, int, int, int]:
        if not text:
            return (0, 0, 0, 0)

        if "\n" in text:
            spacing = self.get_multiline_spacing(font)
            draw = ImageDraw.Draw(Image.new("L", (1, 1), 0))
            bbox = draw.multiline_textbbox(
                (0, 0), text, font=font, spacing=spacing, align="left"
            )
        else:
            bbox = font.getbbox(text)

        if bbox is None:
            return (0, 0, 0, 0)

        return (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))

    def calculate_text_size(
        self, text: str, font: ImageFont.FreeTypeFont
    ) -> tuple[int, int]:
        bbox = self.calculate_text_bbox(text, font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    def get_builtin_fonts(self) -> list[str]:
        font_names = []
        try:
            font_dir = resources.files("mono_pixel.fonts")
            for item in font_dir.iterdir():
                if item.is_file() and item.name.lower().endswith(
                    (".ttf", ".otf", ".ttc", ".otc")
                ):
                    font_names.append(item.name)
        except (ModuleNotFoundError, FileNotFoundError) as e:
            raise ResourceAccessError("Failed to access bundled fonts directory") from e
        except Exception as e:
            raise ResourceAccessError(
                f"Unexpected error while accessing bundled fonts: {e}"
            ) from e
        return sorted(font_names)

    def get_bundled_font_path(self, font_name: str) -> Path:
        try:
            available_fonts = self.get_builtin_fonts()
        except ResourceAccessError as e:
            raise ResourceAccessError(f"Cannot verify font availability: {e}") from e

        if font_name not in available_fonts:
            raise FontNotFoundError(f"Bundled font not found: {font_name}")

        try:
            with resources.path("mono_pixel.fonts", font_name) as font_path:
                return Path(font_path)
        except (ModuleNotFoundError, FileNotFoundError) as e:
            raise ResourceAccessError(
                f"Failed to access font resource: {font_name}"
            ) from e
        except Exception as e:
            raise ResourceAccessError(
                f"Unexpected error accessing font {font_name}: {e}"
            ) from e

    def load_builtin_font(
        self, font_name: str, font_size: int
    ) -> ImageFont.FreeTypeFont:
        font_path = self.get_bundled_font_path(font_name)
        return self.load_font(font_path, font_size)


def get_multiline_spacing(font: ImageFont.FreeTypeFont) -> int:
    """Return an adaptive line spacing for multiline text rendering."""
    ascent, descent = font.getmetrics()
    nominal_size = getattr(font, "size", ascent + descent)
    return max(1, int(nominal_size * 0.18))


def validate_font_file(font_path: str | Path) -> Path:
    """Validate whether a font file is usable."""
    path = Path(font_path)

    if not path.exists():
        raise FontNotFoundError(f"Font file does not exist: {font_path}")

    if not path.is_file():
        raise InvalidFontError(f"Path is not a file: {font_path}")

    supported_extensions = {".ttf", ".otf", ".ttc", ".otc"}
    if path.suffix.lower() not in supported_extensions:
        supported_extensions_text = ", ".join(sorted(supported_extensions))
        raise InvalidFontError(
            "Unsupported font format: "
            f"{path.suffix}. Supported: {supported_extensions_text}"
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
    if not isinstance(font_size, int) or font_size <= 0:
        raise ValueError(f"Font size must be a positive integer, got: {font_size}")

    validated_path = validate_font_file(font_path)

    try:
        return ImageFont.truetype(str(validated_path), font_size)
    except Exception as e:
        raise InvalidFontError(
            f"Failed to load font: {validated_path}. Error: {e}"
        ) from e


def get_font_metrics(font: ImageFont.FreeTypeFont) -> tuple[int, int, int]:
    ascent, descent = font.getmetrics()
    return ascent, descent, ascent + descent


def calculate_text_bbox(
    text: str, font: ImageFont.FreeTypeFont
) -> tuple[int, int, int, int]:
    if not text:
        return (0, 0, 0, 0)

    if "\n" in text:
        spacing = get_multiline_spacing(font)
        draw = ImageDraw.Draw(Image.new("L", (1, 1), 0))
        bbox = draw.multiline_textbbox(
            (0, 0), text, font=font, spacing=spacing, align="left"
        )
    else:
        bbox = font.getbbox(text)

    if bbox is None:
        return (0, 0, 0, 0)

    return (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))


def calculate_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = calculate_text_bbox(text, font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def get_builtin_fonts() -> list[str]:
    font_names = []
    try:
        font_dir = resources.files("mono_pixel.fonts")
        for item in font_dir.iterdir():
            if item.is_file() and item.name.lower().endswith(
                (".ttf", ".otf", ".ttc", ".otc")
            ):
                font_names.append(item.name)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise ResourceAccessError("Failed to access bundled fonts directory") from e
    except Exception as e:
        raise ResourceAccessError(
            f"Unexpected error while accessing bundled fonts: {e}"
        ) from e
    return sorted(font_names)


def get_bundled_font_path(font_name: str) -> Path:
    try:
        available_fonts = get_builtin_fonts()
    except ResourceAccessError as e:
        raise ResourceAccessError(f"Cannot verify font availability: {e}") from e

    if font_name not in available_fonts:
        raise FontNotFoundError(f"Bundled font not found: {font_name}")

    try:
        with resources.path("mono_pixel.fonts", font_name) as font_path:
            return Path(font_path)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise ResourceAccessError(f"Failed to access font resource: {font_name}") from e
    except Exception as e:
        raise ResourceAccessError(
            f"Unexpected error accessing font {font_name}: {e}"
        ) from e


def load_builtin_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
    font_path = get_bundled_font_path(font_name)
    return load_font(font_path, font_size)
