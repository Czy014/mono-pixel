"""mono-pixel command line interface."""

from importlib import import_module

_command_module = import_module("mono_pixel.cli.command")

app = _command_module.app

__all__ = ["app", "cli"]


def cli() -> None:
    """Entrypoint used by the package script."""
    app()


if __name__ == "__main__":
    cli()
