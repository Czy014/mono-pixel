"""Layout pre-validation helpers."""

from dataclasses import dataclass

from .font_loader import FontLoader
from .renderer import Renderer


@dataclass(slots=True)
class LayoutValidationResult:
    warnings: list[str]
    has_errors: bool


class LayoutValidator:
    """Pre-calculate layout constraints before rendering."""

    def __init__(
        self, font_loader: FontLoader | None = None, renderer: Renderer | None = None
    ) -> None:
        self.font_loader = font_loader or FontLoader()
        self.renderer = renderer or Renderer()

    def validate(
        self,
        text: str,
        image_size: tuple[int, int],
        font_path: str,
        font_size: int | None,
        auto_fit: bool,
        padding: int | tuple[int, int, int, int],
    ) -> LayoutValidationResult:
        warnings: list[str] = []
        has_errors = False

        if isinstance(padding, int):
            pad_top = pad_right = pad_bottom = pad_left = padding
        else:
            pad_top, pad_right, pad_bottom, pad_left = padding

        available_width = image_size[0] - pad_left - pad_right
        available_height = image_size[1] - pad_top - pad_bottom

        actual_font_size = font_size
        if auto_fit:
            actual_font_size = self.renderer.calculate_auto_font_size(
                text, font_path, image_size[0], image_size[1], padding
            )

        if actual_font_size is None:
            return LayoutValidationResult(["Could not determine font size"], True)

        font = self.font_loader.load_font(font_path, actual_font_size)
        text_width, text_height = self.font_loader.calculate_text_size(text, font)

        if text_width > available_width:
            warnings.append(
                "Warning: text width "
                f"({text_width}px) exceeds available width ({available_width}px)"
            )
            has_errors = True

        if text_height > available_height:
            warnings.append(
                "Warning: text height "
                f"({text_height}px) exceeds available height ({available_height}px)"
            )
            has_errors = True

        if text_width < available_width * 0.2 and text_height < available_height * 0.2:
            warnings.append(
                "Warning: text size "
                f"({text_width}x{text_height}px) is relatively small for the canvas"
            )

        return LayoutValidationResult(warnings, has_errors)
