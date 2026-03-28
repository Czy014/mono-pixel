"""Dependency checks converted to pytest assertions."""

import importlib.util


def test_pillow_installed() -> None:
    """Pillow should be importable."""
    assert importlib.util.find_spec("PIL") is not None


def test_typer_installed() -> None:
    """Typer should be importable."""
    assert importlib.util.find_spec("typer") is not None
