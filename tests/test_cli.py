"""CLI text normalization tests."""

from mono_pixel.cli import normalize_cli_text


def test_normalize_cli_text_converts_escaped_newline() -> None:
    """Literal "\\n" in CLI input should become a real line break."""
    text = normalize_cli_text("Hello\\nWorld")
    assert text == "Hello\nWorld"


def test_normalize_cli_text_converts_escaped_crlf() -> None:
    """Literal "\\r\\n" should normalize to "\n"."""
    text = normalize_cli_text("A\\r\\nB")
    assert text == "A\nB"


def test_normalize_cli_text_preserves_double_escaped_newline() -> None:
    """Double-escaped newline should remain a visible "\\n" literal."""
    text = normalize_cli_text("Show \\\\n literally")
    assert text == "Show \\n literally"
