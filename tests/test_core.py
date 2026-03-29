"""Core module tests (converted to pytest style)."""

from pathlib import Path

import pytest

from mono_pixel import get_bundled_font_path
from mono_pixel.exporter import save_image, strict_binarization
from mono_pixel.font_loader import (
    FontNotFoundError,
    calculate_text_size,
    get_font_metrics,
    load_font,
    validate_font_file,
)
from mono_pixel.renderer import (
    HorizontalAlign,
    VerticalAlign,
    calculate_text_position,
    create_canvas,
)

TEST_FONT = get_bundled_font_path("pico8-mono.ttf")


def test_validate_font_file_raises_for_missing():
    """validate_font_file should raise for missing font paths."""
    with pytest.raises(FontNotFoundError):
        validate_font_file("/nonexistent/font.ttf")


def test_font_metrics_and_text_size():
    """Loading a font should provide sensible metrics and text size."""
    font = load_font(str(TEST_FONT), 12)
    ascent, descent, line_height = get_font_metrics(font)
    assert isinstance(ascent, int)
    assert isinstance(descent, int)
    assert isinstance(line_height, int)

    text_width, text_height = calculate_text_size("Hello", font)
    assert isinstance(text_width, int)
    assert isinstance(text_height, int)


def test_renderer_create_canvas_and_position():
    """create_canvas and calculate_text_position should work with defaults."""
    canvas = create_canvas(200, 100, "white")
    assert canvas.size == (200, 100)

    font = load_font(str(TEST_FONT), 12)
    x, y = calculate_text_position(
        "Test",
        font,
        200,
        100,
        padding=10,
        align=HorizontalAlign.CENTER,
        valign=VerticalAlign.MIDDLE,
    )
    assert isinstance(x, int) and isinstance(y, int)


def test_exporter_strict_binarization_and_save(tmp_path: Path):
    """strict_binarization should produce 1-bit images.
    save_image should write files to disk.
    """
    canvas = create_canvas(100, 50, "white")
    binary_image = strict_binarization(canvas)
    assert binary_image.mode == "1"

    temp_path = tmp_path / "out.png"
    saved = save_image(canvas, temp_path, strict_binarize=False)
    assert saved.exists()
