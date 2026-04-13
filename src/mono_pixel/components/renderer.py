"""Text rendering module for pixel-style output."""

from enum import StrEnum

from PIL import Image, ImageDraw, ImageFont

from .font_loader import (
    calculate_text_bbox,
    calculate_text_size,
    get_multiline_spacing,
    load_font,
)


class HorizontalAlign(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(StrEnum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class Renderer:
    """Object-oriented renderer facade over module-level render operations."""

    def create_canvas(
        self, width: int, height: int, bg_color: str | tuple[int, int, int] = "white"
    ) -> Image.Image:
        if not isinstance(width, int) or width <= 0:
            raise ValueError(f"Canvas width must be a positive integer, got: {width}")
        if not isinstance(height, int) or height <= 0:
            raise ValueError(f"Canvas height must be a positive integer, got: {height}")
        return Image.new("RGB", (width, height), bg_color)

    def calculate_text_position(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        canvas_width: int,
        canvas_height: int,
        padding: int | tuple[int, int, int, int] = 0,
        align: HorizontalAlign = HorizontalAlign.CENTER,
        valign: VerticalAlign = VerticalAlign.MIDDLE,
    ) -> tuple[int, int]:
        if isinstance(padding, int):
            pad_top = pad_right = pad_bottom = pad_left = padding
        else:
            pad_top, pad_right, pad_bottom, pad_left = padding

        available_width = canvas_width - pad_left - pad_right
        available_height = canvas_height - pad_top - pad_bottom
        bbox = calculate_text_bbox(text, font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if align == HorizontalAlign.LEFT:
            x = pad_left - bbox[0]
        elif align == HorizontalAlign.RIGHT:
            x = canvas_width - pad_right - bbox[2]
        else:
            x = pad_left + (available_width - text_width) // 2 - bbox[0]

        if valign == VerticalAlign.TOP:
            y = pad_top - bbox[1]
        elif valign == VerticalAlign.BOTTOM:
            y = canvas_height - pad_bottom - bbox[3]
        else:
            y = pad_top + (available_height - text_height) // 2 - bbox[1]

        return (x, y)

    def calculate_auto_font_size(
        self,
        text: str,
        font_path: str,
        canvas_width: int,
        canvas_height: int,
        padding: int | tuple[int, int, int, int] = 0,
        min_font_size: int = 8,
        max_font_size: int = 1024,
    ) -> int:
        if isinstance(padding, int):
            pad_top = pad_right = pad_bottom = pad_left = padding
        else:
            pad_top, pad_right, pad_bottom, pad_left = padding

        available_width = canvas_width - pad_left - pad_right
        available_height = canvas_height - pad_top - pad_bottom
        low = min_font_size
        high = max_font_size
        best_size = min_font_size

        while low <= high:
            mid = (low + high) // 2
            try:
                font = load_font(font_path, mid)
                text_width, text_height = calculate_text_size(text, font)
                if text_width <= available_width and text_height <= available_height:
                    best_size = mid
                    low = mid + 1
                else:
                    high = mid - 1
            except Exception:
                high = mid - 1

        return best_size

    def render_pixel_text(
        self,
        canvas: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont,
        position: tuple[int, int],
        fg_color: str | tuple[int, int, int] = "black",
    ) -> Image.Image:
        draw = ImageDraw.Draw(canvas)
        if "\n" in text:
            spacing = get_multiline_spacing(font)
            draw.multiline_text(
                position, text, font=font, fill=fg_color, spacing=spacing, align="left"
            )
        else:
            draw.text(position, text, font=font, fill=fg_color)
        return canvas

    def render_text(
        self,
        text: str,
        font_path: str,
        image_size: tuple[int, int],
        font_size: int | None = None,
        auto_fit: bool = False,
        padding: int | tuple[int, int, int, int] = 16,
        align: HorizontalAlign | str = HorizontalAlign.CENTER,
        valign: VerticalAlign | str = VerticalAlign.MIDDLE,
        bg_color: str | tuple[int, int, int] = "white",
        fg_color: str | tuple[int, int, int] = "black",
    ) -> Image.Image:
        if not text:
            raise ValueError("Text cannot be empty")

        if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
            raise ValueError("Specify exactly one of font_size or auto_fit")

        if isinstance(align, str):
            align = HorizontalAlign(align)
        if isinstance(valign, str):
            valign = VerticalAlign(valign)

        canvas = self.create_canvas(image_size[0], image_size[1], bg_color)

        if auto_fit:
            calculated_font_size = self.calculate_auto_font_size(
                text, font_path, image_size[0], image_size[1], padding
            )
            if calculated_font_size is None:
                raise ValueError("Could not auto-calculate font size")
            font_size = calculated_font_size

        if font_size is None:
            raise ValueError("Font size is required unless auto_fit is enabled")

        font = load_font(font_path, font_size)
        position = self.calculate_text_position(
            text, font, image_size[0], image_size[1], padding, align, valign
        )
        return self.render_pixel_text(canvas, text, font, position, fg_color)


def create_canvas(
    width: int, height: int, bg_color: str | tuple[int, int, int] = "white"
) -> Image.Image:
    if not isinstance(width, int) or width <= 0:
        raise ValueError(f"Canvas width must be a positive integer, got: {width}")
    if not isinstance(height, int) or height <= 0:
        raise ValueError(f"Canvas height must be a positive integer, got: {height}")
    return Image.new("RGB", (width, height), bg_color)


def calculate_text_position(
    text: str,
    font: ImageFont.FreeTypeFont,
    canvas_width: int,
    canvas_height: int,
    padding: int | tuple[int, int, int, int] = 0,
    align: HorizontalAlign = HorizontalAlign.CENTER,
    valign: VerticalAlign = VerticalAlign.MIDDLE,
) -> tuple[int, int]:
    if isinstance(padding, int):
        pad_top = pad_right = pad_bottom = pad_left = padding
    else:
        pad_top, pad_right, pad_bottom, pad_left = padding

    available_width = canvas_width - pad_left - pad_right
    available_height = canvas_height - pad_top - pad_bottom
    bbox = calculate_text_bbox(text, font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if align == HorizontalAlign.LEFT:
        x = pad_left - bbox[0]
    elif align == HorizontalAlign.RIGHT:
        x = canvas_width - pad_right - bbox[2]
    else:
        x = pad_left + (available_width - text_width) // 2 - bbox[0]

    if valign == VerticalAlign.TOP:
        y = pad_top - bbox[1]
    elif valign == VerticalAlign.BOTTOM:
        y = canvas_height - pad_bottom - bbox[3]
    else:
        y = pad_top + (available_height - text_height) // 2 - bbox[1]

    return (x, y)


def calculate_auto_font_size(
    text: str,
    font_path: str,
    canvas_width: int,
    canvas_height: int,
    padding: int | tuple[int, int, int, int] = 0,
    min_font_size: int = 8,
    max_font_size: int = 1024,
) -> int:
    if isinstance(padding, int):
        pad_top = pad_right = pad_bottom = pad_left = padding
    else:
        pad_top, pad_right, pad_bottom, pad_left = padding

    available_width = canvas_width - pad_left - pad_right
    available_height = canvas_height - pad_top - pad_bottom
    low = min_font_size
    high = max_font_size
    best_size = min_font_size

    while low <= high:
        mid = (low + high) // 2
        try:
            font = load_font(font_path, mid)
            text_width, text_height = calculate_text_size(text, font)
            if text_width <= available_width and text_height <= available_height:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        except Exception:
            high = mid - 1

    return best_size


def render_pixel_text(
    canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    position: tuple[int, int],
    fg_color: str | tuple[int, int, int] = "black",
) -> Image.Image:
    draw = ImageDraw.Draw(canvas)
    if "\n" in text:
        spacing = get_multiline_spacing(font)
        draw.multiline_text(
            position, text, font=font, fill=fg_color, spacing=spacing, align="left"
        )
    else:
        draw.text(position, text, font=font, fill=fg_color)
    return canvas


def render_text(
    text: str,
    font_path: str,
    image_size: tuple[int, int],
    font_size: int | None = None,
    auto_fit: bool = False,
    padding: int | tuple[int, int, int, int] = 16,
    align: HorizontalAlign | str = HorizontalAlign.CENTER,
    valign: VerticalAlign | str = VerticalAlign.MIDDLE,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
) -> Image.Image:
    if not text:
        raise ValueError("Text cannot be empty")

    if (font_size is None and not auto_fit) or (font_size is not None and auto_fit):
        raise ValueError("Specify exactly one of font_size or auto_fit")

    if isinstance(align, str):
        align = HorizontalAlign(align)
    if isinstance(valign, str):
        valign = VerticalAlign(valign)

    canvas = create_canvas(image_size[0], image_size[1], bg_color)

    if auto_fit:
        calculated_font_size = calculate_auto_font_size(
            text, font_path, image_size[0], image_size[1], padding
        )
        if calculated_font_size is None:
            raise ValueError("Could not auto-calculate font size")
        font_size = calculated_font_size

    if font_size is None:
        raise ValueError("Font size is required unless auto_fit is enabled")

    font = load_font(font_path, font_size)
    position = calculate_text_position(
        text, font, image_size[0], image_size[1], padding, align, valign
    )
    return render_pixel_text(canvas, text, font, position, fg_color)
