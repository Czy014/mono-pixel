"""Exporter module unit tests."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

from mono_pixel.exporter import (
    convert_to_monochrome,
    export_to_png,
    export_to_svg,
    save_image,
    strict_binarization,
)
from mono_pixel.renderer import create_canvas


class TestStrictBinarization:
    """Tests for strict binarization."""

    def test_basic_binarization(self):
        """Basic binarization behavior."""
        canvas = create_canvas(100, 50, "white")
        result = strict_binarization(canvas)

        assert isinstance(result, Image.Image)
        assert result.mode == "1"  # 1位深度
        assert result.size == (100, 50)

    def test_custom_threshold(self):
        """Custom threshold parameter."""
        canvas = create_canvas(100, 50, "white")
        result = strict_binarization(canvas, threshold=64)

        assert isinstance(result, Image.Image)
        assert result.mode == "1"

    def test_invalid_threshold(self):
        """Invalid threshold values raise ValueError."""
        canvas = create_canvas(100, 50, "white")

        with pytest.raises(ValueError):
            strict_binarization(canvas, threshold=-1)

        with pytest.raises(ValueError):
            strict_binarization(canvas, threshold=256)

    def test_invert_colors(self):
        """Invert colors option works."""
        canvas = create_canvas(100, 50, "white")
        result = strict_binarization(canvas, invert=True)

        assert isinstance(result, Image.Image)
        assert result.mode == "1"

    def test_gray_image(self):
        """Accept grayscale images as input."""
        canvas = create_canvas(100, 50, "white").convert("L")
        result = strict_binarization(canvas)

        assert isinstance(result, Image.Image)
        assert result.mode == "1"


class TestConvertToMonochrome:
    """Convert to monochrome image tests."""

    def test_basic_conversion(self):
        """Basic monochrome conversion."""
        canvas = create_canvas(100, 50, "white")
        result = convert_to_monochrome(canvas, "white", "black")

        assert isinstance(result, Image.Image)
        assert result.mode == "RGB"
        assert result.size == (100, 50)

    def test_custom_colors(self):
        """Support custom color specifications."""
        canvas = create_canvas(100, 50, "white")
        # 使用RGB元组作为颜色
        result = convert_to_monochrome(canvas, (255, 255, 255), (0, 0, 0))

        assert isinstance(result, Image.Image)
        assert result.mode == "RGB"

    def test_custom_threshold(self):
        """Custom threshold for conversion."""
        canvas = create_canvas(100, 50, "white")
        result = convert_to_monochrome(canvas, "white", "black", threshold=192)

        assert isinstance(result, Image.Image)


class TestExportToPng:
    """Export to PNG tests."""

    def test_export_basic(self, temp_output_path: Path):
        """Basic PNG export writes file and is readable."""
        canvas = create_canvas(100, 50, "white")
        result = export_to_png(canvas, temp_output_path)

        assert result == temp_output_path
        assert result.exists()

        # 验证可以打开
        with Image.open(result) as img:
            assert img.size == (100, 50)

    def test_export_with_dpi(self, temp_output_path: Path):
        """测试带DPI导出"""
        canvas = create_canvas(100, 50, "white")
        result = export_to_png(canvas, temp_output_path, dpi=(300, 300))

        assert result.exists()

    def test_export_optimize(self, temp_output_path: Path):
        """测试优化导出"""
        canvas = create_canvas(100, 50, "white")
        result = export_to_png(canvas, temp_output_path, optimize=True)

        assert result.exists()

    def test_export_to_nonexistent_dir(self, tmp_path: Path):
        """测试导出到不存在的目录"""
        canvas = create_canvas(100, 50, "white")
        output_path = tmp_path / "nonexistent" / "output.png"

        # 应该自动创建目录
        result = export_to_png(canvas, output_path)
        assert result.exists()


class TestSaveImage:
    """测试完整保存流程"""

    def test_save_with_binarization(self, temp_output_path: Path):
        """测试带二值化保存"""
        canvas = create_canvas(200, 100, "white")
        result = save_image(
            canvas,
            temp_output_path,
            strict_binarize=True,
            bg_color="white",
            fg_color="black",
        )

        assert result.exists()

        with Image.open(result) as img:
            assert img.size == (200, 100)

    def test_save_without_binarization(self, temp_output_path: Path):
        """测试不带二值化保存"""
        canvas = create_canvas(200, 100, "white")
        result = save_image(canvas, temp_output_path, strict_binarize=False)

        assert result.exists()

    def test_save_with_all_options(self, temp_output_path: Path):
        """测试所有选项"""
        canvas = create_canvas(300, 150, "white")
        result = save_image(
            canvas,
            temp_output_path,
            strict_binarize=True,
            bg_color="white",
            fg_color="black",
            binarization_threshold=127,
            dpi=(150, 150),
            optimize=True,
        )

        assert result.exists()

    def test_save_1bit_mode(self, temp_output_path: Path):
        """测试保存二值化图像"""
        # 先用二值化处理
        canvas = create_canvas(100, 50, "white")
        binarized = strict_binarization(canvas)

        # 保存二值化后的图像
        result = save_image(binarized, temp_output_path, strict_binarize=False)

        assert result.exists()


class TestEdgeCases:
    """测试边界情况"""

    def test_small_image(self, temp_output_path: Path):
        """测试小图像"""
        canvas = create_canvas(16, 16, "white")
        result = save_image(canvas, temp_output_path, strict_binarize=True)
        assert result.exists()

    def test_large_image(self, temp_output_path: Path):
        """测试大图像"""
        canvas = create_canvas(1024, 1024, "white")
        result = save_image(canvas, temp_output_path, strict_binarize=True)
        assert result.exists()


class TestExportToSvg:
    """Tests for SVG export."""

    def test_export_basic(self, tmp_path: Path):
        """Basic SVG export writes valid file."""
        canvas = create_canvas(100, 50, "white")
        output_path = tmp_path / "output.svg"
        result = export_to_svg(canvas, output_path)

        assert result == output_path
        assert result.exists()

        # Verify it's valid XML
        tree = ET.parse(str(result))
        root = tree.getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.attrib["width"] == "100"
        assert root.attrib["height"] == "50"

    def test_export_with_pixel_size(self, tmp_path: Path):
        """Custom pixel size works."""
        canvas = create_canvas(10, 10, "white")
        output_path = tmp_path / "output.svg"
        result = export_to_svg(canvas, output_path, pixel_size=2)

        assert result.exists()

        tree = ET.parse(str(result))
        root = tree.getroot()
        assert root.attrib["width"] == "20"
        assert root.attrib["height"] == "20"

    def test_export_custom_colors(self, tmp_path: Path):
        """Custom colors work."""
        canvas = create_canvas(50, 50, "white")
        output_path = tmp_path / "output.svg"
        result = export_to_svg(canvas, output_path, bg_color="red", fg_color="blue")

        assert result.exists()

        tree = ET.parse(str(result))
        root = tree.getroot()
        # Check background rect has red color
        bg_rect = root.find(".//{http://www.w3.org/2000/svg}rect")
        assert bg_rect is not None
        assert bg_rect.attrib["fill"] == "#ff0000"

    def test_export_with_binarized_image(self, tmp_path: Path):
        """Export binarized image works."""
        canvas = create_canvas(50, 50, "white")
        binarized = strict_binarization(canvas)
        output_path = tmp_path / "output.svg"
        result = export_to_svg(
            binarized, output_path, bg_color="white", fg_color="black"
        )

        assert result.exists()

        tree = ET.parse(str(result))
        root = tree.getroot()
        # Should have background and foreground group
        fg_group = root.find(".//{http://www.w3.org/2000/svg}g")
        assert fg_group is not None

    def test_export_creates_parent_dir(self, tmp_path: Path):
        """Creates non-existent parent directory."""
        canvas = create_canvas(50, 50, "white")
        output_path = tmp_path / "nonexistent" / "output.svg"
        result = export_to_svg(canvas, output_path)

        assert result.exists()


class TestSaveImageSvg:
    """Tests for save_image with SVG format."""

    def test_save_as_svg(self, tmp_path: Path):
        """save_image auto-detects SVG format."""
        canvas = create_canvas(100, 50, "white")
        output_path = tmp_path / "output.svg"
        result = save_image(canvas, output_path)

        assert result.exists()
        assert result.suffix == ".svg"

        # Verify it's valid SVG
        tree = ET.parse(str(result))
        root = tree.getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"

    def test_save_as_svg_with_pixel_size(self, tmp_path: Path):
        """SVG pixel size option works."""
        canvas = create_canvas(10, 10, "white")
        output_path = tmp_path / "output.svg"
        result = save_image(canvas, output_path, svg_pixel_size=3)

        assert result.exists()

        tree = ET.parse(str(result))
        root = tree.getroot()
        assert root.attrib["width"] == "30"
        assert root.attrib["height"] == "30"

    def test_save_png_still_works(self, temp_output_path: Path):
        """PNG export still works after SVG changes."""
        canvas = create_canvas(100, 50, "white")
        result = save_image(canvas, temp_output_path)

        assert result.exists()
        assert result.suffix == ".png"

        with Image.open(result) as img:
            assert img.size == (100, 50)

    def test_save_svg_overrides_format_for_svg_ext(self, tmp_path: Path):
        """Even with PNG options, .svg extension produces SVG."""
        canvas = create_canvas(100, 50, "white")
        output_path = tmp_path / "output.svg"
        result = save_image(
            canvas,
            output_path,
            dpi=(300, 300),  # PNG-only option, ignored for SVG
            svg_pixel_size=2,
        )

        assert result.exists()
        assert result.suffix == ".svg"

        tree = ET.parse(str(result))
        root = tree.getroot()
        assert root.attrib["width"] == "200"

    def test_black_background(self, temp_output_path: Path):
        """测试黑色背景"""
        canvas = create_canvas(200, 100, "black")
        result = save_image(
            canvas,
            temp_output_path,
            strict_binarize=True,
            bg_color="black",
            fg_color="white",
        )
        assert result.exists()
