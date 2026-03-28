"""Integration tests for core APIs and end-to-end workflow."""

from pathlib import Path

from PIL import Image

from mono_pixel import __version__, create_canvas, save_image, strict_binarization


def test_version_present() -> None:
    """The package should expose a non-empty `__version__` string."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_core_api_imports() -> None:
    """Core API functions should be importable and callable."""
    assert callable(create_canvas)
    assert callable(strict_binarization)
    assert callable(save_image)


def test_basic_workflow(tmp_path: Path) -> None:
    """Create a canvas, binarize it and save to disk."""
    canvas = create_canvas(200, 100, "white")
    assert canvas.size == (200, 100)

    binary_image = strict_binarization(canvas)
    assert binary_image.mode == "1"

    out_path = tmp_path / "integration_out.png"
    saved = save_image(canvas, out_path, strict_binarize=False)
    assert saved.exists()

    with Image.open(saved) as img:
        assert img.size == canvas.size
