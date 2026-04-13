"""Pure helpers for resolving CLI-style inputs into core requests."""

from __future__ import annotations

import re
from pathlib import Path

from ..components.font_loader import get_bundled_font_path
from ..components.renderer import HorizontalAlign, VerticalAlign
from .requests import ExportRequest, PipelineRequest, RenderRequest


def parse_image_size(size_str: str) -> tuple[int, int]:
    separators = r"[xX*,\s]+"
    parts = re.split(separators, size_str.strip())
    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {size_str}. Expected e.g. 1024x1024")

    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as exc:
        raise ValueError(
            f"Invalid size format: {size_str}. Expected e.g. 1024x1024"
        ) from exc

    if width <= 0 or height <= 0:
        raise ValueError("Image size must be positive integers")

    return (width, height)


def parse_padding(padding_str: str) -> int | tuple[int, int, int, int]:
    if "," not in padding_str:
        try:
            return int(padding_str)
        except ValueError as exc:
            raise ValueError(f"Invalid padding format: {padding_str}") from exc

    parts = padding_str.split(",")
    if len(parts) == 2:
        try:
            vertical = int(parts[0].strip())
            horizontal = int(parts[1].strip())
            return (vertical, horizontal, vertical, horizontal)
        except ValueError as exc:
            raise ValueError(f"Invalid padding format: {padding_str}") from exc

    if len(parts) == 4:
        try:
            top = int(parts[0].strip())
            right = int(parts[1].strip())
            bottom = int(parts[2].strip())
            left = int(parts[3].strip())
            return (top, right, bottom, left)
        except ValueError as exc:
            raise ValueError(f"Invalid padding format: {padding_str}") from exc

    raise ValueError(
        f"Invalid padding format: {padding_str}. Use '16', '10,20', or '10,20,30,40'"
    )


def normalize_cli_text(text: str) -> str:
    literal_newline_token = "\x00MONO_PIXEL_LITERAL_BACKSLASH_N\x00"
    normalized = text.replace("\\\\n", literal_newline_token)
    normalized = normalized.replace("\\r\\n", "\n")
    normalized = normalized.replace("\\n", "\n")
    return normalized.replace(literal_newline_token, "\\n")


def build_pipeline_request(
    *,
    text: str,
    image_size: str | tuple[int, int],
    font_path: str | Path | None = None,
    builtin_font: str | None = None,
    font_size: int | None = None,
    auto_fit: bool = False,
    padding: str | int | tuple[int, int, int, int] = 16,
    align: HorizontalAlign | str = HorizontalAlign.CENTER,
    valign: VerticalAlign | str = VerticalAlign.MIDDLE,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    output_path: str | Path | None = None,
    no_binarization: bool = False,
    binarization_threshold: int = 127,
    dpi: int = 72,
) -> PipelineRequest:
    if isinstance(image_size, str):
        resolved_image_size = parse_image_size(image_size)
    else:
        resolved_image_size = image_size

    if isinstance(padding, str):
        resolved_padding = parse_padding(padding)
    else:
        resolved_padding = padding

    if font_path is not None and builtin_font is not None:
        raise ValueError("Specify exactly one of font_path or builtin_font")

    if font_path is None and builtin_font is None:
        raise ValueError("Specify exactly one of font_path or builtin_font")

    if font_path is None and builtin_font is not None:
        font_path = get_bundled_font_path(builtin_font)

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        raise ValueError("Specify exactly one of font_size or auto_fit")

    render_request = RenderRequest(
        text=text,
        font_path=str(font_path),
        image_size=resolved_image_size,
        font_size=font_size,
        auto_fit=auto_fit,
        padding=resolved_padding,
        align=align,
        valign=valign,
        bg_color=bg_color,
        fg_color=fg_color,
    )

    export_request = None
    if output_path is not None:
        export_request = ExportRequest(
            output_path=output_path,
            strict_binarize=not no_binarization,
            bg_color=bg_color,
            fg_color=fg_color,
            binarization_threshold=binarization_threshold,
            dpi=(dpi, dpi),
            optimize=True,
        )

    return PipelineRequest(render=render_request, export=export_request)
