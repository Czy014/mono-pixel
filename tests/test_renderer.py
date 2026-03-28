"""Renderer module unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from mono_pixel.renderer import (
    HorizontalAlign,
    VerticalAlign,
    calculate_auto_font_size,
    calculate_text_position,
    create_canvas,
    render_pixel_text,
    render_text,
)


class TestCreateCanvas:
    """Test canvas creation."""

    def test_create_canvas(self):
        """Create a canvas with the given size and background."""
        canvas = create_canvas(200, 100, "white")
        assert isinstance(canvas, Image.Image)
        assert canvas.size == (200, 100)
        assert canvas.mode == "RGB"

    def test_invalid_size(self):
        """Invalid sizes should raise ValueError."""
        with pytest.raises(ValueError):
            create_canvas(0, 100)

        with pytest.raises(ValueError):
            create_canvas(200, 0)

        with pytest.raises(ValueError):
            create_canvas(-200, 100)

    def test_custom_bg_color(self):
        """Custom background color should be applied to canvas."""
        canvas = create_canvas(100, 100, "black")
        # 检查左上角像素是否为黑色
        pixel = canvas.getpixel((0, 0))
        assert pixel == (0, 0, 0)


class TestCalculateTextPosition:
    """Text position calculation tests."""

    def test_center_alignment(self, test_font_path: Path, sample_text: str):
        """Center alignment computes integer coordinates."""
        from mono_pixel.font_loader import load_font

        font = load_font(test_font_path, 32)
        x, y = calculate_text_position(
            sample_text,
            font,
            200,
            100,
            10,
            HorizontalAlign.CENTER,
            VerticalAlign.MIDDLE,
        )
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_left_alignment(self, test_font_path: Path, sample_text: str):
        """Left alignment computes integer coordinates."""
        from mono_pixel.font_loader import load_font

        font = load_font(test_font_path, 32)
        x, y = calculate_text_position(
            sample_text, font, 200, 100, 10, HorizontalAlign.LEFT, VerticalAlign.MIDDLE
        )
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_right_alignment(self, test_font_path: Path, sample_text: str):
        """Right alignment computes integer coordinates."""
        from mono_pixel.font_loader import load_font

        font = load_font(test_font_path, 32)
        x, y = calculate_text_position(
            sample_text, font, 200, 100, 10, HorizontalAlign.RIGHT, VerticalAlign.MIDDLE
        )
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_different_paddings(self, test_font_path: Path, sample_text: str):
        """Different padding formats are supported."""
        from mono_pixel.font_loader import load_font

        font = load_font(test_font_path, 32)

        # single-value padding
        x1, y1 = calculate_text_position(sample_text, font, 200, 100, 10)

        # four-tuple padding
        x2, y2 = calculate_text_position(sample_text, font, 200, 100, (10, 10, 10, 10))

        assert isinstance(x1, int)
        assert isinstance(y1, int)
        assert isinstance(x2, int)
        assert isinstance(y2, int)


class TestCalculateAutoFontSize:
    """Auto font size calculation tests."""

    def test_auto_fit_basic(self, test_font_path: Path, sample_text: str):
        """Basic auto-fit should return a positive integer font size."""
        font_size = calculate_auto_font_size(
            sample_text, str(test_font_path), 512, 256, 16
        )
        assert isinstance(font_size, int)
        assert font_size > 0
        assert font_size <= 256  # 不应该超过画布高度

    def test_auto_fit_small_canvas(self, test_font_path: Path):
        """Auto-fit on small canvas should still return a positive size."""
        font_size = calculate_auto_font_size("Hi", str(test_font_path), 64, 64, 8)
        assert isinstance(font_size, int)
        assert font_size > 0

    def test_auto_fit_large_text(self, test_font_path: Path):
        """Auto-fit for long text should return a positive size."""
        long_text = "This is a very long text that should fit properly"
        font_size = calculate_auto_font_size(
            long_text, str(test_font_path), 1024, 256, 16
        )
        assert isinstance(font_size, int)
        assert font_size > 0


class TestRenderPixelText:
    """Pixel text rendering tests."""

    def test_render_basic(self, test_font_path: Path, sample_text: str):
        """Basic pixel rendering returns a valid image."""
        from mono_pixel.font_loader import load_font

        canvas = create_canvas(512, 256, "white")
        font = load_font(test_font_path, 64)
        position = (50, 50)

        result = render_pixel_text(canvas, sample_text, font, position, "black")
        assert isinstance(result, Image.Image)
        assert result.size == (512, 256)

    def test_different_colors(self, test_font_path: Path):
        """Rendering supports different foreground/background colors."""
        from mono_pixel.font_loader import load_font

        canvas = create_canvas(200, 100, "black")
        font = load_font(test_font_path, 32)

        result = render_pixel_text(canvas, "Test", font, (10, 10), "white")
        assert isinstance(result, Image.Image)


class TestRenderText:
    """Full render_text workflow tests."""

    def test_render_with_font_size(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Rendering with explicit font size."""
        result = render_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=image_size,
            font_size=64,
            auto_fit=False,
        )
        assert isinstance(result, Image.Image)
        assert result.size == image_size

    def test_render_with_auto_fit(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Rendering with auto-fit enabled."""
        result = render_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=image_size,
            font_size=None,
            auto_fit=True,
        )
        assert isinstance(result, Image.Image)
        assert result.size == image_size

    def test_render_with_custom_options(self, test_font_path: Path, sample_text: str):
        """Rendering with custom options (padding, align, colors)."""
        result = render_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(400, 200),
            font_size=48,
            auto_fit=False,
            padding=20,
            align=HorizontalAlign.LEFT,
            valign=VerticalAlign.TOP,
            bg_color="white",
            fg_color="black",
        )
        assert isinstance(result, Image.Image)
        assert result.size == (400, 200)

    def test_invalid_parameters(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Invalid render parameters should raise ValueError."""
        # 同时指定font_size和auto_fit
        with pytest.raises(ValueError):
            render_text(
                text=sample_text,
                font_path=str(test_font_path),
                image_size=image_size,
                font_size=64,
                auto_fit=True,
            )

        # 都不指定
        with pytest.raises(ValueError):
            render_text(
                text=sample_text,
                font_path=str(test_font_path),
                image_size=image_size,
                font_size=None,
                auto_fit=False,
            )

        # 空文字
        with pytest.raises(ValueError):
            render_text(
                text="",
                font_path=str(test_font_path),
                image_size=image_size,
                auto_fit=True,
            )


class TestAlignmentEnums:
    """Alignment enum tests."""

    def test_horizontal_align_values(self):
        """Horizontal alignment enum values."""
        assert HorizontalAlign.LEFT == "left"
        assert HorizontalAlign.CENTER == "center"
        assert HorizontalAlign.RIGHT == "right"

    def test_vertical_align_values(self):
        """Vertical alignment enum values."""
        assert VerticalAlign.TOP == "top"
        assert VerticalAlign.MIDDLE == "middle"
        assert VerticalAlign.BOTTOM == "bottom"

    def test_enum_from_string(self):
        """Enums can be created from strings."""
        assert HorizontalAlign("left") == HorizontalAlign.LEFT
        assert VerticalAlign("middle") == VerticalAlign.MIDDLE
