"""
核心API集成测试
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from mono_pixel import (
    FontNotFoundError,
    HorizontalAlign,
    InvalidFontError,
    VerticalAlign,
    __version__,
    create_canvas,
    generate_pixel_text,
    load_font,
    render_text,
    save_image,
    strict_binarization,
    validate_font_file,
)


class TestVersion:
    """Version information tests."""

    def test_version_exists(self):
        """The package exposes a non-empty version string."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestImports:
    """API import tests."""

    def test_all_imports_available(self):
        """All public API symbols are importable."""
        # 这些应该都可以从mono_pixel直接导入
        # 如果能导入到这里，说明没问题
        assert True


class TestGeneratePixelText:
    """High-level generate_pixel_text API tests."""

    def test_generate_with_font_size(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Generate image with explicit font size."""
        result = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=image_size,
            font_size=64,
            auto_fit=False,
        )
        assert isinstance(result, Image.Image)
        assert result.size == image_size

    def test_generate_with_auto_fit(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Generate image using auto-fit font sizing."""
        result = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=image_size,
            font_size=None,
            auto_fit=True,
        )
        assert isinstance(result, Image.Image)
        assert result.size == image_size

    def test_generate_and_save(
        self, test_font_path: Path, sample_text: str, temp_output_path: Path
    ):
        """Generate an image and save to disk."""
        result = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(512, 256),
            auto_fit=True,
            output_path=str(temp_output_path),
        )
        assert isinstance(result, Image.Image)
        assert temp_output_path.exists()

    def test_generate_with_custom_options(self, test_font_path: Path, sample_text: str):
        """Generate with custom rendering options."""
        result = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(400, 200),
            font_size=48,
            auto_fit=False,
            padding=30,
            align=HorizontalAlign.RIGHT,
            valign=VerticalAlign.BOTTOM,
            bg_color="white",
            fg_color="black",
            strict_binarize=True,
            binarization_threshold=127,
        )
        assert isinstance(result, Image.Image)
        assert result.size == (400, 200)

    def test_generate_without_binarization(
        self, test_font_path: Path, sample_text: str
    ):
        """Generate without applying strict binarization."""
        result = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(256, 128),
            auto_fit=True,
            strict_binarize=False,
        )
        assert isinstance(result, Image.Image)

    def test_invalid_parameters(
        self, test_font_path: Path, sample_text: str, image_size: tuple[int, int]
    ):
        """Invalid parameter combinations raise ValueError."""
        # 同时指定font_size和auto_fit
        with pytest.raises(ValueError):
            generate_pixel_text(
                text=sample_text,
                font_path=str(test_font_path),
                image_size=image_size,
                font_size=64,
                auto_fit=True,
            )

        # 都不指定
        with pytest.raises(ValueError):
            generate_pixel_text(
                text=sample_text,
                font_path=str(test_font_path),
                image_size=image_size,
                font_size=None,
                auto_fit=False,
            )

        # 空文字
        with pytest.raises(ValueError):
            generate_pixel_text(
                text="",
                font_path=str(test_font_path),
                image_size=image_size,
                auto_fit=True,
            )

        # 无效字体路径
        with pytest.raises(FontNotFoundError):
            generate_pixel_text(
                text=sample_text,
                font_path="/nonexistent/font.ttf",
                image_size=image_size,
                auto_fit=True,
            )


class TestLowLevelAPI:
    """Low-level API tests."""

    def test_validate_font_file(self, test_font_path: Path):
        """validate_font_file returns the given Path when valid."""
        result = validate_font_file(test_font_path)
        assert result == test_font_path

    def test_load_font(self, test_font_path: Path):
        """load_font returns a usable font object."""
        font = load_font(test_font_path, 32)
        assert font is not None

    def test_create_canvas(self):
        """create_canvas yields an image with the expected size."""
        canvas = create_canvas(200, 100, "white")
        assert canvas.size == (200, 100)

    def test_strict_binarization(self):
        """strict_binarization produces a 1-bit image."""
        canvas = create_canvas(100, 50, "white")
        result = strict_binarization(canvas)
        assert result.mode == "1"

    def test_render_text(self, test_font_path: Path, sample_text: str):
        """render_text returns a Pillow Image when rendering text."""
        result = render_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(256, 128),
            auto_fit=True,
        )
        assert isinstance(result, Image.Image)

    def test_save_image(self, temp_output_path: Path):
        """save_image writes the image file to disk."""
        canvas = create_canvas(100, 50, "white")
        result = save_image(canvas, temp_output_path, strict_binarize=False)
        assert result.exists()


class TestEnums:
    """Enum behavior tests."""

    def test_horizontal_align(self):
        """HorizontalAlign enum string values and construction."""
        assert HorizontalAlign.LEFT == "left"
        assert HorizontalAlign.CENTER == "center"
        assert HorizontalAlign.RIGHT == "right"

        # 测试从字符串创建
        assert HorizontalAlign("left") == HorizontalAlign.LEFT

    def test_vertical_align(self):
        """VerticalAlign enum string values and construction."""
        assert VerticalAlign.TOP == "top"
        assert VerticalAlign.MIDDLE == "middle"
        assert VerticalAlign.BOTTOM == "bottom"

        # 测试从字符串创建
        assert VerticalAlign("middle") == VerticalAlign.MIDDLE


class TestExceptions:
    """Exception type tests."""

    def test_font_not_found_error(self):
        """FontNotFoundError can be raised and caught."""
        with pytest.raises(FontNotFoundError):
            raise FontNotFoundError("测试")

    def test_invalid_font_error(self):
        """InvalidFontError can be raised and caught."""
        with pytest.raises(InvalidFontError):
            raise InvalidFontError("测试")


class TestIntegration:
    """Integration tests covering end-to-end flows."""

    def test_full_workflow(
        self, test_font_path: Path, sample_text: str, temp_output_path: Path
    ):
        """Full end-to-end workflow: generate, save, reopen."""
        # 1. 生成图像
        image = generate_pixel_text(
            text=sample_text,
            font_path=str(test_font_path),
            image_size=(512, 256),
            auto_fit=True,
        )

        # 2. 验证图像
        assert isinstance(image, Image.Image)
        assert image.size == (512, 256)

        # 3. 保存图像
        saved_path = save_image(image, temp_output_path, strict_binarize=True)

        # 4. 验证保存
        assert saved_path.exists()

        # 5. 重新打开验证
        with Image.open(saved_path) as img:
            assert img.size == (512, 256)
