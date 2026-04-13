"""Font loader module unit tests."""

from pathlib import Path

import pytest
from PIL import ImageFont

from mono_pixel.components.font_loader import (
    FontError,
    FontNotFoundError,
    InvalidFontError,
    calculate_text_bbox,
    calculate_text_size,
    get_font_metrics,
    load_font,
    validate_font_file,
)


class TestValidateFontFile:
    """Validate font file behavior."""

    def test_valid_font(self, test_font_path: Path):
        """validate_font_file accepts a valid font path."""
        result = validate_font_file(test_font_path)
        assert result == test_font_path

    def test_nonexistent_file(self):
        """Missing file raises FontNotFoundError."""
        with pytest.raises(FontNotFoundError):
            validate_font_file("/nonexistent/font.ttf")

    def test_not_a_file(self, tmp_path: Path):
        """Non-file paths raise InvalidFontError."""
        with pytest.raises(InvalidFontError):
            validate_font_file(tmp_path)

    def test_invalid_extension(self, tmp_path: Path):
        """Unsupported extensions raise InvalidFontError."""
        invalid_file = tmp_path / "font.txt"
        invalid_file.touch()
        with pytest.raises(InvalidFontError):
            validate_font_file(invalid_file)

    def test_file_too_small(self, tmp_path: Path):
        """Too-small files are rejected."""
        small_file = tmp_path / "small.ttf"
        small_file.write_bytes(b"x" * 500)  # 小于1KB
        with pytest.raises(InvalidFontError):
            validate_font_file(small_file)


class TestLoadFont:
    """Font loading tests."""

    def test_load_valid_font(self, test_font_path: Path):
        """load_font returns a FreeTypeFont for valid fonts."""
        font = load_font(test_font_path, 32)
        assert isinstance(font, ImageFont.FreeTypeFont)

    def test_invalid_font_size(self, test_font_path: Path):
        """Invalid font sizes raise ValueError."""
        with pytest.raises(ValueError):
            load_font(test_font_path, 0)

        with pytest.raises(ValueError):
            load_font(test_font_path, -10)

    def test_nonexistent_font(self):
        """Loading a missing font raises FontNotFoundError."""
        with pytest.raises(FontNotFoundError):
            load_font("/nonexistent/font.ttf", 32)


class TestFontMetrics:
    """Font metrics tests."""

    def test_get_font_metrics(self, test_font_path: Path):
        """get_font_metrics returns ascent, descent and line height."""
        font = load_font(test_font_path, 32)
        ascent, descent, line_height = get_font_metrics(font)

        assert isinstance(ascent, int)
        assert isinstance(descent, int)
        assert isinstance(line_height, int)
        assert line_height == ascent + descent

    def test_calculate_text_bbox(self, test_font_path: Path, sample_text: str):
        """calculate_text_bbox returns a valid bounding box."""
        font = load_font(test_font_path, 32)
        bbox = calculate_text_bbox(sample_text, font)

        assert len(bbox) == 4
        left, top, right, bottom = bbox
        assert left <= right
        assert top <= bottom

    def test_calculate_text_size(self, test_font_path: Path, sample_text: str):
        """calculate_text_size returns width and height for text."""
        font = load_font(test_font_path, 32)
        width, height = calculate_text_size(sample_text, font)

        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width >= 0
        assert height >= 0

    def test_empty_text(self, test_font_path: Path):
        """Empty text returns numeric width/height values."""
        font = load_font(test_font_path, 32)
        width, height = calculate_text_size("", font)
        # 空文字可能返回0或某个最小值，取决于字体
        assert isinstance(width, int)
        assert isinstance(height, int)


class TestExceptions:
    """Exception hierarchy tests."""

    def test_exception_hierarchy(self):
        """Font exceptions inherit from base FontError."""
        assert issubclass(FontNotFoundError, FontError)
        assert issubclass(InvalidFontError, FontError)
