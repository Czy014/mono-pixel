"""Tests for built-in fonts functionality."""

import pytest

from mono_pixel import (
    FontNotFoundError,
    get_builtin_fonts,
    get_bundled_font_path,
    load_builtin_font,
)


def test_get_builtin_fonts():
    """Test getting list of built-in fonts."""
    fonts = get_builtin_fonts()
    assert isinstance(fonts, list)
    # Should have at least our two test fonts
    assert len(fonts) >= 2
    assert "pico8-mono.ttf" in fonts
    assert "pixel32.ttf" in fonts


def test_get_bundled_font_path_valid():
    """Test getting path to a valid bundled font."""
    path = get_bundled_font_path("pico8-mono.ttf")
    assert path.exists()
    assert path.is_file()
    assert path.suffix.lower() == ".ttf"


def test_get_bundled_font_path_invalid():
    """Test getting path to a non-existent bundled font."""
    with pytest.raises(FontNotFoundError):
        get_bundled_font_path("nonexistent-font.ttf")


def test_load_builtin_font_valid():
    """Test loading a valid built-in font."""
    font = load_builtin_font("pico8-mono.ttf", 12)
    assert font is not None
    # Verify it's a valid font by checking metrics
    ascent, descent = font.getmetrics()
    assert ascent > 0


def test_load_builtin_font_invalid():
    """Test loading a non-existent built-in font."""
    with pytest.raises(FontNotFoundError):
        load_builtin_font("nonexistent-font.ttf", 12)


def test_load_builtin_font_invalid_size():
    """Test loading with invalid font size."""
    with pytest.raises(ValueError):
        load_builtin_font("pico8-mono.ttf", 0)
    with pytest.raises(ValueError):
        load_builtin_font("pico8-mono.ttf", -10)
