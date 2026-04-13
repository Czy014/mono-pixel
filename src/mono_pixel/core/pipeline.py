"""Stateless pipeline implementation for mono-pixel rendering."""

from __future__ import annotations

from ..components.layout_validator import LayoutValidator
from .abstractions import ExporterBase, FontLoaderBase, PipelineBase, RendererBase
from .components import DefaultExporter, DefaultFontLoader, DefaultRenderer
from .requests import PipelineRequest
from .results import PipelineResult


class PipelineEngine(PipelineBase):
    """Pipeline-first orchestration of validate/load/render/export."""

    def __init__(
        self,
        font_loader: FontLoaderBase | None = None,
        renderer: RendererBase | None = None,
        exporter: ExporterBase | None = None,
        layout_validator: LayoutValidator | None = None,
    ) -> None:
        self.font_loader = font_loader or DefaultFontLoader()
        self.renderer = renderer or DefaultRenderer()
        self.exporter = exporter or DefaultExporter()
        self.layout_validator = layout_validator or LayoutValidator()

    def run(self, request: PipelineRequest) -> PipelineResult:
        request.validate()
        render_request = request.render

        resolved_font_size = render_request.font_size
        if render_request.auto_fit:
            resolved_font_size = self.renderer.calculate_auto_font_size(
                text=render_request.text,
                font_path=render_request.font_path,
                canvas_width=render_request.image_size[0],
                canvas_height=render_request.image_size[1],
                padding=render_request.padding,
            )

        if resolved_font_size is None:
            raise ValueError("Could not resolve font size for rendering")

        validation_result = self.layout_validator.validate(
            text=render_request.text,
            image_size=render_request.image_size,
            font_path=render_request.font_path,
            font_size=resolved_font_size,
            auto_fit=render_request.auto_fit,
            padding=render_request.padding,
        )

        self.font_loader.load_font(render_request.font_path, resolved_font_size)

        image = self.renderer.render(
            text=render_request.text,
            font_path=render_request.font_path,
            image_size=render_request.image_size,
            font_size=resolved_font_size,
            padding=render_request.padding,
            align=render_request.align,
            valign=render_request.valign,
            bg_color=render_request.bg_color,
            fg_color=render_request.fg_color,
        )

        export_path = None
        if request.export is not None:
            export_path = self.exporter.save(
                image=image,
                output_path=request.export.output_path,
                strict_binarize=request.export.strict_binarize,
                bg_color=request.export.bg_color,
                fg_color=request.export.fg_color,
                binarization_threshold=request.export.binarization_threshold,
                dpi=request.export.dpi,
                optimize=request.export.optimize,
                svg_pixel_size=request.export.svg_pixel_size,
            )

        return PipelineResult(
            image=image,
            render_request=render_request,
            export_path=export_path,
            warnings=tuple(validation_result.warnings),
            resolved_font_size=resolved_font_size,
        )
