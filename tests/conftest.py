"""Pytest common configuration and fixtures."""

from pathlib import Path

import pytest

from mono_pixel import get_bundled_font_path


@pytest.fixture
def test_font_path() -> Path:
    """Path to a test TrueType font (using built-in font)."""
    return get_bundled_font_path("pico8-mono.ttf")


@pytest.fixture
def sample_text() -> str:
    """Sample text used across tests."""
    return "Hello Pixel"


@pytest.fixture
def image_size() -> tuple[int, int]:
    """Default image size for tests (width, height)."""
    return (512, 256)


@pytest.fixture
def temp_output_path(tmp_path: Path) -> Path:
    """Temporary output file path for tests."""
    return tmp_path / "output.png"
