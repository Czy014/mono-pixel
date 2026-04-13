"""CLI run-command integration tests."""

from pathlib import Path

from typer.testing import CliRunner

from mono_pixel.cli import app

runner = CliRunner()


def test_run_command_renders_and_saves_png(
    test_font_path: Path,
    tmp_path: Path,
) -> None:
    """run should generate and save an output image with minimal required options."""
    output_path = tmp_path / "cli-basic.png"

    result = runner.invoke(
        app,
        [
            "run",
            "--text",
            "Hello",
            "--image-size",
            "320x160",
            "--font-path",
            str(test_font_path),
            "--font-size",
            "24",
            "--output",
            str(output_path),
            "--force",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()


def test_run_command_preview_mode_does_not_save(
    test_font_path: Path,
    tmp_path: Path,
) -> None:
    """--preview should skip persistence even when output path is provided."""
    output_path = tmp_path / "cli-preview.png"

    result = runner.invoke(
        app,
        [
            "run",
            "--text",
            "Hello",
            "--image-size",
            "320x160",
            "--font-path",
            str(test_font_path),
            "--font-size",
            "24",
            "--preview",
            "--output",
            str(output_path),
            "--force",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert not output_path.exists()


def test_run_rejects_font_path_and_builtin_font_together(
    test_font_path: Path,
) -> None:
    """font source options should remain mutually exclusive."""
    result = runner.invoke(
        app,
        [
            "run",
            "--text",
            "Hello",
            "--image-size",
            "320x160",
            "--font-path",
            str(test_font_path),
            "--builtin-font",
            "pico8-mono.ttf",
            "--font-size",
            "24",
            "--force",
            "--quiet",
        ],
    )

    assert result.exit_code != 0
    assert "mutually exclusive" in result.stdout.lower()


def test_run_rejects_font_size_and_auto_fit_together(test_font_path: Path) -> None:
    """font size mode options should remain mutually exclusive."""
    result = runner.invoke(
        app,
        [
            "run",
            "--text",
            "Hello",
            "--image-size",
            "320x160",
            "--font-path",
            str(test_font_path),
            "--font-size",
            "24",
            "--auto-fit",
            "--force",
            "--quiet",
        ],
    )

    assert result.exit_code != 0
    assert "exactly one of --font-size or --auto-fit" in result.stdout


def test_run_rejects_invalid_image_size(test_font_path: Path) -> None:
    """invalid image-size format should fail before rendering."""
    result = runner.invoke(
        app,
        [
            "run",
            "--text",
            "Hello",
            "--image-size",
            "320x",
            "--font-path",
            str(test_font_path),
            "--font-size",
            "24",
            "--force",
            "--quiet",
        ],
    )

    assert result.exit_code == 2
