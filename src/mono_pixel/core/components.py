"""Default component implementations backed by concrete components."""

from pathlib import Path

from PIL import Image, ImageFont

from ..components.exporter import ImageExporter
from ..components.font_loader import FontLoader
from ..components.renderer import HorizontalAlign, Renderer, VerticalAlign


class DefaultFontLoader:
    """Font loader implementation that delegates to existing font utilities."""

    def __init__(self, loader: FontLoader | None = None) -> None:
        self.loader = loader or FontLoader()

    def load_font(
        self, font_path: str | Path, font_size: int
    ) -> ImageFont.FreeTypeFont:
        return self.loader.load_font(font_path, font_size)

    def calculate_text_size(
        self, text: str, font: ImageFont.FreeTypeFont
    ) -> tuple[int, int]:
        return self.loader.calculate_text_size(text, font)


class DefaultRenderer:
    """Renderer implementation that keeps current rendering behavior."""

    def __init__(self, renderer: Renderer | None = None) -> None:
        self.renderer = renderer or Renderer()

    def calculate_auto_font_size(
        self,
        text: str,
        font_path: str,
        canvas_width: int,
        canvas_height: int,
        padding: int | tuple[int, int, int, int],
    ) -> int:
        return self.renderer.calculate_auto_font_size(
            text=text,
            font_path=font_path,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            padding=padding,
        )

    def render(
        self,
        text: str,
        font_path: str,
        image_size: tuple[int, int],
        font_size: int,
        padding: int | tuple[int, int, int, int],
        align: HorizontalAlign | str,
        valign: VerticalAlign | str,
        bg_color: str | tuple[int, int, int],
        fg_color: str | tuple[int, int, int],
    ) -> Image.Image:
        return self.renderer.render_text(
            text=text,
            font_path=font_path,
            image_size=image_size,
            font_size=font_size,
            auto_fit=False,
            padding=padding,
            align=align,
            valign=valign,
            bg_color=bg_color,
            fg_color=fg_color,
        )


class DefaultExporter:
    """Exporter implementation that delegates to existing export utilities."""

    def __init__(self, exporter: ImageExporter | None = None) -> None:
        self.exporter = exporter or ImageExporter()

    def save(
        self,
        image: Image.Image,
        output_path: str | Path,
        strict_binarize: bool = True,
        bg_color: str | tuple[int, int, int] = "white",
        fg_color: str | tuple[int, int, int] = "black",
        binarization_threshold: int = 127,
        dpi: tuple[int, int] = (72, 72),
        optimize: bool = True,
        svg_pixel_size: int = 1,
    ) -> Path:
        return self.exporter.save_image(
            image=image,
            output_path=output_path,
            strict_binarize=strict_binarize,
            bg_color=bg_color,
            fg_color=fg_color,
            binarization_threshold=binarization_threshold,
            dpi=dpi,
            optimize=optimize,
            svg_pixel_size=svg_pixel_size,
        )
