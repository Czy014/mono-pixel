"""Typer command entry points for mono-pixel."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .. import __version__
from ..components.font_loader import get_builtin_fonts
from ..components.renderer import HorizontalAlign, VerticalAlign
from ..core import PipelineEngine, build_pipeline_request, normalize_cli_text
from ..utils.exceptions import ResourceAccessError
from .presenter import CLIPresenter

app = typer.Typer(
    name="mono-pixel", help="High-fidelity pixel text renderer.", add_completion=False
)
cli = app
console = Console()
DEFAULT_OUTPUT_PATH = Path("output.png")


class MonoPixelRunCommand:
    """Backwards-compatible command helper used by tests and the Typer app."""

    @staticmethod
    def parse_image_size(size_str: str) -> tuple[int, int]:
        from ..core.input_resolver import parse_image_size

        return parse_image_size(size_str)

    @staticmethod
    def parse_padding(padding_str: str) -> int | tuple[int, int, int, int]:
        from ..core.input_resolver import parse_padding

        return parse_padding(padding_str)

    @staticmethod
    def normalize_cli_text(text: str) -> str:
        return normalize_cli_text(text)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"mono-pixel version {__version__}")
        raise typer.Exit()


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
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(code=0)


@app.command("list-fonts")
def list_fonts_command(
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Quiet mode")] = False,
) -> None:
    try:
        fonts = get_builtin_fonts()
    except ResourceAccessError as e:
        console.print(f"[red]Failed to access built-in fonts: {e}[/red]")
        raise typer.Exit(1) from e

    presenter = CLIPresenter(console, quiet=quiet)
    presenter.print_fonts(fonts)
    if not fonts:
        raise typer.Exit(0)


def _prompt_interactive_inputs(
    text: str | None,
    text_file: Path | None,
    font_path: Path | None,
    builtin_font: str | None,
    image_size: str | None,
    font_size: int | None,
    auto_fit: bool,
    output: Path,
    quiet: bool,
) -> tuple[
    str | None, Path | None, Path | None, str | None, str | None, int | None, bool, Path
]:
    if not quiet:
        console.print("[bold blue]Interactive mode[/bold blue]\n")

    if text is None:
        text_source = Prompt.ask(
            "Text source", choices=["direct", "file"], default="direct"
        )
        if text_source == "file":
            text_file = Path(Prompt.ask("Text file path"))
        else:
            text = Prompt.ask("Text to render")

    if font_path is None and builtin_font is None:
        try:
            builtin_fonts = get_builtin_fonts()
        except ResourceAccessError:
            builtin_fonts = []
        if builtin_fonts:
            font_choice = Prompt.ask(
                "Font source", choices=["builtin", "custom"], default="builtin"
            )
            if font_choice == "builtin":
                for index, font in enumerate(builtin_fonts, 1):
                    console.print(f"  {index}. {font}")
                builtin_index = int(Prompt.ask("Select font number", default="1")) - 1
                builtin_font = builtin_fonts[builtin_index]
            else:
                font_path = Path(Prompt.ask("TTF/OTF font path"))
        else:
            font_path = Path(Prompt.ask("TTF/OTF font path"))

    if image_size is None:
        image_size = Prompt.ask("Image size", default="1024x1024")

    if font_size is None and not auto_fit:
        size_choice = Prompt.ask(
            "Font size mode", choices=["manual", "auto"], default="auto"
        )
        if size_choice == "manual":
            font_size = int(Prompt.ask("Font size (px)", default="64"))
            auto_fit = False
        else:
            auto_fit = True

    if output == DEFAULT_OUTPUT_PATH:
        output = Path(Prompt.ask("Output file path", default="output.png"))

    return (
        text,
        text_file,
        font_path,
        builtin_font,
        image_size,
        font_size,
        auto_fit,
        output,
    )


@app.command("run")
def run_command(
    text: Annotated[
        str | None,
        typer.Option("--text", "-t", help="Text to render", rich_help_panel="Core"),
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
            "--preview-ascii", help="Show ASCII preview only", rich_help_panel="Preview"
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
                "Output file path (.png for raster, .svg for vector; "
                "default: output.png)"
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
            "--fg-color", help="Foreground text color", rich_help_panel="Layout"
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
        int, typer.Option("--dpi", help="Output image DPI", rich_help_panel="Output")
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
        bool, typer.Option("--quiet", "-q", help="Quiet mode", rich_help_panel="Output")
    ] = False,
) -> None:
    if (
        text is None
        and text_file is None
        and image_size is None
        and font_path is None
        and builtin_font is None
    ):
        (
            text,
            text_file,
            font_path,
            builtin_font,
            image_size,
            font_size,
            auto_fit,
            output,
        ) = _prompt_interactive_inputs(
            text,
            text_file,
            font_path,
            builtin_font,
            image_size,
            font_size,
            auto_fit,
            output,
            quiet,
        )

    if text_file is not None:
        try:
            text = text_file.read_text(encoding="utf-8").strip()
        except Exception as exc:
            console.print(f"[red]Failed to read text file: {exc}[/red]")
            raise typer.Exit(1) from exc

    text = normalize_cli_text(text or "")
    if not text:
        console.print("[red]Error: text cannot be empty[/red]")
        raise typer.Exit(1)

    if image_size is None:
        console.print("[red]Error: --image-size is required[/red]")
        raise typer.Exit(1)

    if font_path is not None and builtin_font is not None:
        console.print(
            "[red]Error: --font-path and --builtin-font are mutually exclusive[/red]"
        )
        raise typer.Exit(1)

    if font_path is None and builtin_font is None:
        console.print("[red]Error: specify either --font-path or --builtin-font[/red]")
        raise typer.Exit(1)

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        console.print(
            "[red]Error: specify exactly one of --font-size or --auto-fit[/red]"
        )
        raise typer.Exit(1)

    try:
        request = build_pipeline_request(
            text=text,
            image_size=image_size,
            font_path=font_path,
            builtin_font=builtin_font,
            font_size=font_size,
            auto_fit=auto_fit,
            padding=padding,
            align=align,
            valign=valign,
            bg_color=bg_color,
            fg_color=fg_color,
            output_path=None if preview else output,
            no_binarization=no_binarization,
            binarization_threshold=binarization_threshold,
            dpi=dpi,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(2) from exc

    pipeline = PipelineEngine()
    presenter = CLIPresenter(console, quiet=quiet)

    if not force:
        if not quiet and output.exists() and not overwrite and not preview:
            if not Confirm.ask(
                f"Output file exists: {output}. Overwrite?", default=False
            ):
                console.print("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(5)

    try:
        result = pipeline.run(request)
    except Exception as exc:
        console.print(f"[red]Render failed: {exc}[/red]")
        raise typer.Exit(3) from exc

    if result.warnings and not quiet and not force:
        for warning in result.warnings:
            console.print(warning)

    if not force and not no_preview:
        presenter.print_preview(
            result.image, request.render.image_size, preview_ascii=preview_ascii
        )

    if preview_image and not quiet:
        console.print("\n[dim]Image preview support is not available yet in v0.1[/dim]")

    if preview:
        if not quiet:
            console.print("\n[green]Preview completed, no file saved[/green]")
        raise typer.Exit()

    if no_preview:
        pass
    elif not force and not Confirm.ask("\nSave output image?", default=True):
        console.print("[yellow]Operation cancelled[/yellow]")
        raise typer.Exit(5)

    if result.export_path is not None and not quiet:
        console.print(f"\n[green]Saved successfully: {result.export_path}[/green]")
    elif not quiet:
        console.print(f"\n[bold]Saving image to: {output}[/bold]")
