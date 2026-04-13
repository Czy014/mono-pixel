"""Terminal presentation helpers for CLI output."""

from rich.console import Console

from ..components.previewer import Previewer


class CLIPresenter:
    """Render previews and status output."""

    def __init__(self, console: Console, quiet: bool = False) -> None:
        self.console = console
        self.quiet = quiet
        self.previewer = Previewer()

    def print_fonts(self, fonts: list[str]) -> None:
        if not fonts:
            self.console.print("[yellow]No built-in fonts available[/yellow]")
            return

        if not self.quiet:
            self.console.print("[bold]Available built-in fonts:[/bold]\n")
        for font in fonts:
            self.console.print(f"  - {font}")

    def print_preview(
        self, image, image_size: tuple[int, int], preview_ascii: bool = False
    ) -> None:
        if self.quiet:
            return

        preview_width = min(80, max(20, self.console.size.width - 4))
        if preview_ascii:
            self.console.print("\n[bold]ASCII preview (raw):[/bold]")
            self.console.print(
                self.previewer.generate_ascii_preview(image, preview_width)
            )
        else:
            self.console.print("\n[bold]ASCII preview (position-aware):[/bold]")
            self.console.print(
                self.previewer.build_position_aware_preview(
                    image, image_size, preview_width
                )
            )
