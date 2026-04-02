"""mono-pixel command line interface."""

import re
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from . import __version__
from .exporter import save_image
from .font_loader import (
    calculate_text_size,
    get_builtin_fonts,
    get_bundled_font_path,
    load_font,
)
from .renderer import (
    HorizontalAlign,
    VerticalAlign,
    calculate_auto_font_size,
    render_text,
)
from .utils.exceptions import FontNotFoundError, InvalidFontError, ResourceAccessError
from .utils.preview import (
    build_position_aware_preview,
    generate_ascii_preview,
)

app = typer.Typer(
    name="mono-pixel",
    help="High-fidelity pixel text renderer.",
    add_completion=False,
)
console = Console()
DEFAULT_OUTPUT_PATH = Path("output.png")


def version_callback(value: bool) -> None:
    """Handle global version option."""
    if value:
        console.print(f"mono-pixel version {__version__}")
        raise typer.Exit()


def parse_image_size(size_str: str) -> tuple[int, int]:
    """Parse image size string.

    Supported formats: 1024x1024, 1024*1024, 1024 1024.
    """
    separators = r"[xX*,\s]+"
    parts = re.split(separators, size_str.strip())

    if len(parts) != 2:
        raise typer.BadParameter(
            f"Invalid size format: {size_str}. Expected e.g. 1024x1024"
        )

    try:
        width = int(parts[0])
        height = int(parts[1])

        if width <= 0 or height <= 0:
            raise typer.BadParameter("Image size must be positive integers")

        return (width, height)
    except ValueError as exc:
        raise typer.BadParameter(
            f"Invalid size format: {size_str}. Expected e.g. 1024x1024"
        ) from exc


def parse_padding(padding_str: str) -> int | tuple[int, int, int, int]:
    """Parse padding string.

    Supported formats:
    - 16          -> all sides
    - 10,20       -> vertical,horizontal
    - 10,20,30,40 -> top,right,bottom,left
    """
    if "," not in padding_str:
        try:
            return int(padding_str)
        except ValueError as exc:
            raise typer.BadParameter(f"Invalid padding format: {padding_str}") from exc

    parts = padding_str.split(",")
    if len(parts) == 2:
        try:
            vertical = int(parts[0].strip())
            horizontal = int(parts[1].strip())
            return (vertical, horizontal, vertical, horizontal)
        except ValueError as exc:
            raise typer.BadParameter(f"Invalid padding format: {padding_str}") from exc
    elif len(parts) == 4:
        try:
            p1 = int(parts[0].strip())
            p2 = int(parts[1].strip())
            p3 = int(parts[2].strip())
            p4 = int(parts[3].strip())
            return (p1, p2, p3, p4)
        except ValueError as exc:
            raise typer.BadParameter(f"Invalid padding format: {padding_str}") from exc
    else:
        raise typer.BadParameter(
            f"Invalid padding format: {padding_str}. "
            "Use '16', '10,20', or '10,20,30,40'"
        )


# preview helpers have been moved to `mono_pixel.utils.preview`


def pre_validate_layout(
    text: str,
    image_size: tuple[int, int],
    font_path: str | None = None,
    builtin_font: str | None = None,
    font_size: int | None = None,
    auto_fit: bool = False,
    padding: int | tuple[int, int, int, int] = 16,
) -> tuple[bool, list[str]]:
    """Pre-validate layout and return (has_errors, warnings)."""
    warnings = []
    has_errors = False

    # Determine actual font path
    actual_font_path: str
    if font_path is not None:
        actual_font_path = font_path
    elif builtin_font is not None:
        actual_font_path = str(get_bundled_font_path(builtin_font))
    else:
        # This should not happen due to validation before calling this function
        raise ValueError("Either font_path or builtin_font must be provided")

    if isinstance(padding, int):
        pad_top = pad_right = pad_bottom = pad_left = padding
    else:
        pad_top, pad_right, pad_bottom, pad_left = padding

    available_width = image_size[0] - pad_left - pad_right
    available_height = image_size[1] - pad_top - pad_bottom

    actual_font_size = font_size
    if auto_fit:
        actual_font_size = calculate_auto_font_size(
            text, actual_font_path, image_size[0], image_size[1], padding
        )

    if actual_font_size is None:
        return True, ["Could not determine font size"]

    font = load_font(actual_font_path, actual_font_size)
    text_width, text_height = calculate_text_size(text, font)

    if text_width > available_width:
        warnings.append(
            f"Warning: text width ({text_width}px) exceeds "
            f"available width ({available_width}px)"
        )
        has_errors = True

    if text_height > available_height:
        warnings.append(
            f"Warning: text height ({text_height}px) exceeds "
            f"available height ({available_height}px)"
        )
        has_errors = True

    if text_width < available_width * 0.2 and text_height < available_height * 0.2:
        warnings.append(
            f"Warning: text size ({text_width}x{text_height}px) "
            "is relatively small for the canvas"
        )

    return has_errors, warnings


@app.callback(invoke_without_command=True)
def app_callback(
    ctx: typer.Context,
    _version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """mono-pixel top-level command group."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@app.command("list-fonts")
def list_fonts_command(
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Quiet mode")] = False,
) -> None:
    """List available built-in fonts."""
    try:
        fonts = get_builtin_fonts()
    except ResourceAccessError as e:
        console.print(f"[red]Failed to access built-in fonts: {e}[/red]")
        raise typer.Exit(1) from e

    if not fonts:
        console.print("[yellow]No built-in fonts available[/yellow]")
        raise typer.Exit(0)

    if not quiet:
        console.print("[bold]Available built-in fonts:[/bold]\n")
    for font in fonts:
        console.print(f"  - {font}")


@app.command("run")
def run_command(
    text: Annotated[
        str | None,
        typer.Option(
            "--text",
            "-t",
            help="Text to render",
            rich_help_panel="Core",
        ),
    ] = None,
    text_file: Annotated[
        Path | None,
        typer.Option(
            "--text-file",
            help="Read text from a file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            rich_help_panel="Core",
        ),
    ] = None,
    image_size: Annotated[
        str | None,
        typer.Option(
            "--image-size",
            "-s",
            help="Output image size, e.g. 1024x1024",
            rich_help_panel="Core",
        ),
    ] = None,
    font_path: Annotated[
        Path | None,
        typer.Option(
            "--font-path",
            "-f",
            help="Path to TTF/OTF font file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            rich_help_panel="Core",
        ),
    ] = None,
    builtin_font: Annotated[
        str | None,
        typer.Option(
            "--builtin-font",
            "-b",
            help="Use a built-in font (use list-fonts to see available options)",
            rich_help_panel="Core",
        ),
    ] = None,
    font_size: Annotated[
        int | None,
        typer.Option(
            "--font-size",
            "-z",
            help="Manual font size in pixels (mutually exclusive with --auto-fit)",
            rich_help_panel="Core",
        ),
    ] = None,
    auto_fit: Annotated[
        bool,
        typer.Option(
            "--auto-fit",
            "-a",
            help="Auto-fit font size to canvas (mutually exclusive with --font-size)",
            rich_help_panel="Core",
        ),
    ] = False,
    preview: Annotated[
        bool,
        typer.Option(
            "--preview",
            "-p",
            help="Preview only; do not save output file",
            rich_help_panel="Preview",
        ),
    ] = False,
    preview_ascii: Annotated[
        bool,
        typer.Option(
            "--preview-ascii",
            help="Show ASCII preview only",
            rich_help_panel="Preview",
        ),
    ] = False,
    preview_image: Annotated[
        bool,
        typer.Option(
            "--preview-image",
            help="Force image preview (fallback to ASCII if unavailable)",
            rich_help_panel="Preview",
        ),
    ] = False,
    no_preview: Annotated[
        bool,
        typer.Option(
            "--no-preview",
            help="Disable preview and continue directly",
            rich_help_panel="Preview",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Skip validation, preview, and confirmation",
            rich_help_panel="Preview",
        ),
    ] = False,
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help=(
                "Output file path (.png for raster, "
                ".svg for vector; default: output.png)"
            ),
            writable=True,
            rich_help_panel="Output",
        ),
    ] = DEFAULT_OUTPUT_PATH,
    padding: Annotated[
        str,
        typer.Option(
            "--padding",
            "-P",
            help="Padding: '16', '10,20', or '10,20,30,40'",
            rich_help_panel="Layout",
        ),
    ] = "16",
    align: Annotated[
        HorizontalAlign,
        typer.Option("--align", help="Horizontal alignment", rich_help_panel="Layout"),
    ] = HorizontalAlign.CENTER,
    valign: Annotated[
        VerticalAlign,
        typer.Option("--valign", help="Vertical alignment", rich_help_panel="Layout"),
    ] = VerticalAlign.MIDDLE,
    bg_color: Annotated[
        str,
        typer.Option("--bg-color", help="Background color", rich_help_panel="Layout"),
    ] = "white",
    fg_color: Annotated[
        str,
        typer.Option(
            "--fg-color",
            help="Foreground text color",
            rich_help_panel="Layout",
        ),
    ] = "black",
    no_binarization: Annotated[
        bool,
        typer.Option(
            "--no-binarization",
            help="Disable strict binarization",
            rich_help_panel="Binarization",
        ),
    ] = False,
    binarization_threshold: Annotated[
        int,
        typer.Option(
            "--binarization-threshold",
            min=0,
            max=255,
            help="Binarization threshold (0-255)",
            rich_help_panel="Binarization",
        ),
    ] = 127,
    dpi: Annotated[
        int,
        typer.Option("--dpi", help="Output image DPI", rich_help_panel="Output"),
    ] = 72,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite existing output file",
            rich_help_panel="Output",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Quiet mode", rich_help_panel="Output"),
    ] = False,
) -> None:
    """Render pixel text image."""

    if (
        text is None
        and text_file is None
        and image_size is None
        and font_path is None
        and builtin_font is None
    ):
        if not quiet:
            console.print("[bold blue]Interactive mode[/bold blue]\n")

        if text is None:
            text_source = Prompt.ask(
                "Text source", choices=["direct", "file"], default="direct"
            )
            if text_source == "file":
                text_file = Path(Prompt.ask("Text file path"))
                if not text_file.exists():
                    console.print(f"[red]Error: file does not exist: {text_file}[/red]")
                    raise typer.Exit(1)
            else:
                text = Prompt.ask("Text to render")

        if font_path is None and builtin_font is None:
            try:
                builtin_fonts = get_builtin_fonts()
            except ResourceAccessError as e:
                console.print(
                    f"[yellow]Warning: Could not access built-in fonts: {e}[/yellow]"
                )
                builtin_fonts = []

            if builtin_fonts:
                font_choice = Prompt.ask(
                    "Font source",
                    choices=["builtin", "custom"],
                    default="builtin",
                )
                if font_choice == "builtin":
                    console.print("\nAvailable built-in fonts:")
                    for i, font in enumerate(builtin_fonts, 1):
                        console.print(f"  {i}. {font}")
                    font_idx = int(Prompt.ask("Select font number", default="1")) - 1
                    if 0 <= font_idx < len(builtin_fonts):
                        builtin_font = builtin_fonts[font_idx]
                    else:
                        console.print("[red]Invalid font selection[/red]")
                        raise typer.Exit(1)
                else:
                    font_path = Path(Prompt.ask("TTF/OTF font path"))
                    if not font_path.exists():
                        console.print(
                            f"[red]Error: font file does not exist: {font_path}[/red]"
                        )
                        raise typer.Exit(1)
            else:
                font_path = Path(Prompt.ask("TTF/OTF font path"))
                if not font_path.exists():
                    console.print(
                        f"[red]Error: font file does not exist: {font_path}[/red]"
                    )
                    raise typer.Exit(1)

        if image_size is None:
            image_size = Prompt.ask("Image size", default="1024x1024")

        size_choice = Prompt.ask(
            "Font size mode", choices=["manual", "auto"], default="auto"
        )
        if size_choice == "manual":
            font_size = int(Prompt.ask("Font size (px)", default="64"))
            auto_fit = False
        else:
            font_size = None
            auto_fit = True

        if not preview:
            output_str = Prompt.ask("Output file path", default="output.png")
            output = Path(output_str)

    if text_file is not None and isinstance(text_file, Path):
        try:
            text = text_file.read_text(encoding="utf-8").strip()
        except Exception as e:
            console.print(f"[red]Failed to read text file: {e}[/red]")
            raise typer.Exit(1) from e

    if not text:
        console.print("[red]Error: text cannot be empty[/red]")
        raise typer.Exit(1)

    if image_size is None:
        console.print("[red]Error: --image-size is required[/red]")
        raise typer.Exit(1)

    if font_path is None and builtin_font is None:
        console.print("[red]Error: specify either --font-path or --builtin-font[/red]")
        raise typer.Exit(1)

    if font_path is not None and builtin_font is not None:
        console.print(
            "[red]Error: --font-path and --builtin-font are mutually exclusive[/red]"
        )
        raise typer.Exit(1)

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        console.print(
            "[red]Error: specify exactly one of --font-size or --auto-fit[/red]"
        )
        raise typer.Exit(1)

    # Determine actual font path
    actual_font_path: str
    if font_path is not None:
        actual_font_path = str(font_path)
    elif builtin_font is not None:
        actual_font_path = str(get_bundled_font_path(builtin_font))
    else:
        # This should not happen due to earlier validation
        raise ValueError("Either font_path or builtin_font must be provided")

    try:
        parsed_image_size = parse_image_size(image_size)
        parsed_padding = parse_padding(padding)
    except typer.BadParameter as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e

    if not preview and not force and output.exists():
        if not overwrite:
            if not Confirm.ask(
                f"Output file exists: {output}. Overwrite?", default=False
            ):
                console.print("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(5)

    if not force:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=quiet,
            ) as progress:
                progress.add_task("Validating layout...", total=None)
                has_errors, warnings = pre_validate_layout(
                    text=text,
                    image_size=parsed_image_size,
                    font_path=str(font_path) if font_path is not None else None,
                    builtin_font=builtin_font,
                    font_size=font_size,
                    auto_fit=auto_fit,
                    padding=parsed_padding,
                )

            if warnings and not quiet:
                for warning in warnings:
                    console.print(warning)

                if has_errors and not Confirm.ask(
                    "\nPotential layout issues detected. Continue?", default=False
                ):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(5)

        except Exception as e:
            console.print(f"[red]Layout validation failed: {e}[/red]")
            if not Confirm.ask("Continue rendering anyway?", default=False):
                raise typer.Exit(1) from e

    try:
        if not quiet:
            console.print("\n[bold]Rendering image...[/bold]")

        image = render_text(
            text=text,
            font_path=actual_font_path,
            image_size=parsed_image_size,
            font_size=font_size,
            auto_fit=auto_fit,
            padding=parsed_padding,
            align=align,
            valign=valign,
            bg_color=bg_color,
            fg_color=fg_color,
        )

    except FontNotFoundError as e:
        console.print(f"[red]Font file not found: {e}[/red]")
        raise typer.Exit(2) from e
    except InvalidFontError as e:
        console.print(f"[red]Invalid font file: {e}[/red]")
        raise typer.Exit(2) from e
    except Exception as e:
        console.print(f"[red]Render failed: {e}[/red]")
        raise typer.Exit(3) from e

    if not force and not no_preview:
        if not quiet:
            console.print("\n[bold]Generating preview...[/bold]")

        max_preview_width = max(20, console.size.width - 4)
        preview_width = min(80, max_preview_width)
        preview_text = build_position_aware_preview(
            image=image,
            image_size=parsed_image_size,
            preview_width=preview_width,
        )
        if preview_ascii and not quiet:
            ascii_only = generate_ascii_preview(image, preview_width)
            console.print("\n[bold]ASCII preview (raw):[/bold]")
            console.print(ascii_only)
        else:
            console.print("\n[bold]ASCII preview (position-aware):[/bold]")
            console.print(preview_text)

        if preview_image and not quiet:
            console.print(
                "\n[dim]Image preview support is not available yet in v0.1[/dim]"
            )

        if not preview and not Confirm.ask("\nSave output image?", default=True):
            console.print("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(5)

    if preview:
        if not quiet:
            console.print("\n[green]Preview completed, no file saved[/green]")
        raise typer.Exit()

    try:
        if not quiet:
            console.print(f"\n[bold]Saving image to: {output}[/bold]")

        save_image(
            image=image,
            output_path=str(output),
            strict_binarize=not no_binarization,
            bg_color=bg_color,
            fg_color=fg_color,
            binarization_threshold=binarization_threshold,
            dpi=(dpi, dpi),
            optimize=True,
        )

        if not quiet:
            console.print(f"\n[green]Saved successfully: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Failed to save image: {e}[/red]")
        raise typer.Exit(4) from e


def cli() -> None:
    """Entrypoint used by the package script."""
    app()


if __name__ == "__main__":
    cli()
