"""Core pipeline architecture tests."""

from pathlib import Path

from PIL import Image

from mono_pixel.core import (
    ExportRequest,
    PipelineEngine,
    PipelineRequest,
    PipelineResult,
    RenderRequest,
)


def test_pipeline_run_without_export(test_font_path: Path, sample_text: str) -> None:
    """Pipeline should render and return image when export is omitted."""
    request = PipelineRequest(
        render=RenderRequest(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(320, 160),
            font_size=24,
            auto_fit=False,
            padding=12,
        )
    )

    result = PipelineEngine().run(request)
    assert isinstance(result, PipelineResult)
    assert isinstance(result.image, Image.Image)
    assert result.image.size == (320, 160)


def test_pipeline_run_with_export(
    test_font_path: Path,
    sample_text: str,
    tmp_path: Path,
) -> None:
    """Pipeline should export image when export request is provided."""
    output_path = tmp_path / "pipeline-output.png"
    request = PipelineRequest(
        render=RenderRequest(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(256, 128),
            font_size=20,
            auto_fit=False,
            padding=8,
        ),
        export=ExportRequest(
            output_path=output_path,
            strict_binarize=True,
            bg_color="white",
            fg_color="black",
            binarization_threshold=127,
            dpi=(72, 72),
        ),
    )

    result = PipelineEngine().run(request)
    assert isinstance(result, PipelineResult)
    assert isinstance(result.image, Image.Image)
    assert output_path.exists()


def test_pipeline_auto_fit(test_font_path: Path, sample_text: str) -> None:
    """Pipeline should resolve font size when auto_fit is enabled."""
    request = PipelineRequest(
        render=RenderRequest(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(360, 160),
            font_size=None,
            auto_fit=True,
            padding=16,
        )
    )

    result = PipelineEngine().run(request)
    assert isinstance(result, PipelineResult)
    assert isinstance(result.image, Image.Image)
    assert result.image.size == (360, 160)
