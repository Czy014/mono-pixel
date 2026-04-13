"""Typed request models for stateless pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..components.renderer import HorizontalAlign, VerticalAlign


@dataclass(slots=True)
class RenderRequest:
    """All inputs required to render text into an image."""

    text: str
    font_path: str
    image_size: tuple[int, int]
    font_size: int | None = None
    auto_fit: bool = False
    padding: int | tuple[int, int, int, int] = 16
    align: HorizontalAlign | str = HorizontalAlign.CENTER
    valign: VerticalAlign | str = VerticalAlign.MIDDLE
    bg_color: str | tuple[int, int, int] = "white"
    fg_color: str | tuple[int, int, int] = "black"

    def validate(self) -> None:
        if not self.text:
            raise ValueError("Text cannot be empty")

        if (self.font_size is None and not self.auto_fit) or (
            self.font_size is not None and self.auto_fit
        ):
            raise ValueError("Specify exactly one of font_size or auto_fit")

        if self.image_size[0] <= 0 or self.image_size[1] <= 0:
            raise ValueError("Image dimensions must be positive integers")


@dataclass(slots=True)
class ExportRequest:
    """All inputs required to export a rendered image."""

    output_path: str | Path
    strict_binarize: bool = True
    bg_color: str | tuple[int, int, int] = "white"
    fg_color: str | tuple[int, int, int] = "black"
    binarization_threshold: int = 127
    dpi: tuple[int, int] = (72, 72)
    optimize: bool = True
    svg_pixel_size: int = 1

    def validate(self) -> None:
        if not (0 <= self.binarization_threshold <= 255):
            raise ValueError("binarization_threshold must be in [0, 255]")


@dataclass(slots=True)
class PipelineRequest:
    """Top-level request for the stateless pipeline."""

    render: RenderRequest
    export: ExportRequest | None = None

    def validate(self) -> None:
        self.render.validate()
        if self.export is not None:
            self.export.validate()
