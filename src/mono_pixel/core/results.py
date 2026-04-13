"""Structured results returned by the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from .requests import RenderRequest


@dataclass(slots=True)
class PipelineResult:
    """Outcome of a full pipeline run."""

    image: Image.Image
    render_request: RenderRequest
    export_path: Path | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    resolved_font_size: int | None = None
