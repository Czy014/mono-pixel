"""Image export and binarization utilities."""

import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from ..utils.exceptions import ExportError


class ImageExporter:
    """Object-oriented facade for export operations."""

    def strict_binarization(
        self, image: Image.Image, threshold: int = 127, invert: bool = False
    ) -> Image.Image:
        if not (0 <= threshold <= 255):
            raise ValueError(f"Threshold must be in [0, 255], got: {threshold}")

        gray_image = image.convert("L") if image.mode != "L" else image
        width, height = gray_image.size
        binary_data = []

        for y in range(height):
            for x in range(width):
                pixel = gray_image.getpixel((x, y))
                if isinstance(pixel, int):
                    pixel_value = pixel
                elif isinstance(pixel, float):
                    pixel_value = int(pixel)
                elif isinstance(pixel, tuple) and len(pixel) > 0:
                    pixel_value = int(pixel[0])
                else:
                    pixel_value = 0

                if invert:
                    binary_pixel = 0 if pixel_value > threshold else 1
                else:
                    binary_pixel = 1 if pixel_value > threshold else 0
                binary_data.append(binary_pixel)

        binary_image = Image.new("1", (width, height))
        binary_image.putdata(binary_data)
        return binary_image

    def convert_to_monochrome(
        self,
        image: Image.Image,
        bg_color: str | tuple[int, int, int] = "white",
        fg_color: str | tuple[int, int, int] = "black",
        threshold: int = 127,
    ) -> Image.Image:
        binary_image = self.strict_binarization(image, threshold)
        width, height = binary_image.size
        result_image = Image.new("RGB", (width, height), bg_color)

        def parse_color(color):
            if isinstance(color, str):
                from PIL import ImageColor

                return ImageColor.getrgb(color)
            return color

        bg_rgb = parse_color(bg_color)
        fg_rgb = parse_color(fg_color)

        for y in range(height):
            for x in range(width):
                pixel = binary_image.getpixel((x, y))
                result_image.putpixel((x, y), fg_rgb if pixel == 0 else bg_rgb)

        return result_image

    def export_to_png(
        self,
        image: Image.Image,
        output_path: str | Path,
        dpi: tuple[int, int] = (72, 72),
        optimize: bool = True,
    ) -> Path:
        output_path = Path(output_path)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ExportError(
                f"Failed to create output directory: {output_path.parent}. Error: {e}"
            ) from e

        try:
            image.save(str(output_path), format="PNG", dpi=dpi, optimize=optimize)
        except Exception as e:
            raise ExportError(
                f"Failed to save PNG file: {output_path}. Error: {e}"
            ) from e

        return output_path

    def save_image(
        self,
        image: Image.Image,
        output_path: str | Path,
        strict_binarize: bool = True,
        bg_color: str | tuple[int, int, int] = "white",
        fg_color: str | tuple[int, int, int] = "black",
        binarization_threshold: int = 127,
        dpi: tuple[int, int] = (72, 72),
        optimize: bool = True,
        svg_pixel_size: int = 1,
    ) -> Path:
        output_path = Path(output_path)
        processed_image = (
            self.convert_to_monochrome(
                image, bg_color, fg_color, binarization_threshold
            )
            if strict_binarize
            else image
        )
        if output_path.suffix.lower() == ".svg":
            return self.export_to_svg(
                processed_image,
                output_path,
                bg_color=bg_color,
                fg_color=fg_color,
                pixel_size=svg_pixel_size,
            )
        return self.export_to_png(processed_image, output_path, dpi, optimize)

    def export_to_svg(
        self,
        image: Image.Image,
        output_path: str | Path,
        bg_color: str | tuple[int, int, int] = "white",
        fg_color: str | tuple[int, int, int] = "black",
        pixel_size: int = 1,
    ) -> Path:
        output_path = Path(output_path)

        def parse_color(color):
            if isinstance(color, str):
                from PIL import ImageColor

                rgb = ImageColor.getrgb(color)
                return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            if isinstance(color, tuple) and len(color) >= 3:
                return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            return str(color)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ExportError(
                f"Failed to create output directory: {output_path.parent}. Error: {e}"
            ) from e

        bg_svg = parse_color(bg_color)
        fg_svg = parse_color(fg_color)
        width, height = image.size
        svg_width = width * pixel_size
        svg_height = height * pixel_size

        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": str(svg_width),
                "height": str(svg_height),
                "viewBox": f"0 0 {svg_width} {svg_height}",
            },
        )
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(svg_width),
                "height": str(svg_height),
                "fill": bg_svg,
            },
        )
        fg_group = ET.SubElement(svg, "g", {"fill": fg_svg})

        if image.mode == "1":
            for y in range(height):
                for x in range(width):
                    if image.getpixel((x, y)) == 0:
                        ET.SubElement(
                            fg_group,
                            "rect",
                            {
                                "x": str(x * pixel_size),
                                "y": str(y * pixel_size),
                                "width": str(pixel_size),
                                "height": str(pixel_size),
                            },
                        )
        elif image.mode == "L":
            for y in range(height):
                for x in range(width):
                    pixel = image.getpixel((x, y))
                    if isinstance(pixel, int) and pixel < 128:
                        ET.SubElement(
                            fg_group,
                            "rect",
                            {
                                "x": str(x * pixel_size),
                                "y": str(y * pixel_size),
                                "width": str(pixel_size),
                                "height": str(pixel_size),
                            },
                        )
        else:
            for y in range(height):
                for x in range(width):
                    pixel = image.getpixel((x, y))
                    if (
                        isinstance(pixel, tuple)
                        and len(pixel) >= 3
                        and pixel[:3] != (255, 255, 255)
                    ):
                        ET.SubElement(
                            fg_group,
                            "rect",
                            {
                                "x": str(x * pixel_size),
                                "y": str(y * pixel_size),
                                "width": str(pixel_size),
                                "height": str(pixel_size),
                            },
                        )

        tree = ET.ElementTree(svg)
        try:
            tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
        except Exception as e:
            raise ExportError(
                f"Failed to save SVG file: {output_path}. Error: {e}"
            ) from e
        return output_path


def strict_binarization(
    image: Image.Image, threshold: int = 127, invert: bool = False
) -> Image.Image:
    if not (0 <= threshold <= 255):
        raise ValueError(f"Threshold must be in [0, 255], got: {threshold}")

    gray_image = image.convert("L") if image.mode != "L" else image
    width, height = gray_image.size
    binary_data = []

    for y in range(height):
        for x in range(width):
            pixel = gray_image.getpixel((x, y))
            if isinstance(pixel, int):
                pixel_value = pixel
            elif isinstance(pixel, float):
                pixel_value = int(pixel)
            elif isinstance(pixel, tuple) and len(pixel) > 0:
                pixel_value = int(pixel[0])
            else:
                pixel_value = 0

            if invert:
                binary_pixel = 0 if pixel_value > threshold else 1
            else:
                binary_pixel = 1 if pixel_value > threshold else 0
            binary_data.append(binary_pixel)

    binary_image = Image.new("1", (width, height))
    binary_image.putdata(binary_data)
    return binary_image


def convert_to_monochrome(
    image: Image.Image,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    threshold: int = 127,
) -> Image.Image:
    binary_image = strict_binarization(image, threshold)
    width, height = binary_image.size
    result_image = Image.new("RGB", (width, height), bg_color)

    def parse_color(color):
        if isinstance(color, str):
            from PIL import ImageColor

            return ImageColor.getrgb(color)
        return color

    bg_rgb = parse_color(bg_color)
    fg_rgb = parse_color(fg_color)

    for y in range(height):
        for x in range(width):
            pixel = binary_image.getpixel((x, y))
            result_image.putpixel((x, y), fg_rgb if pixel == 0 else bg_rgb)

    return result_image


def export_to_png(
    image: Image.Image,
    output_path: str | Path,
    dpi: tuple[int, int] = (72, 72),
    optimize: bool = True,
) -> Path:
    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ExportError(
            f"Failed to create output directory: {output_path.parent}. Error: {e}"
        ) from e

    try:
        image.save(str(output_path), format="PNG", dpi=dpi, optimize=optimize)
    except Exception as e:
        raise ExportError(f"Failed to save PNG file: {output_path}. Error: {e}") from e

    return output_path


def save_image(
    image: Image.Image,
    output_path: str | Path,
    strict_binarize: bool = True,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    binarization_threshold: int = 127,
    dpi: tuple[int, int] = (72, 72),
    optimize: bool = True,
    svg_pixel_size: int = 1,
) -> Path:
    output_path = Path(output_path)
    processed_image = (
        convert_to_monochrome(image, bg_color, fg_color, binarization_threshold)
        if strict_binarize
        else image
    )
    if output_path.suffix.lower() == ".svg":
        return export_to_svg(
            processed_image,
            output_path,
            bg_color=bg_color,
            fg_color=fg_color,
            pixel_size=svg_pixel_size,
        )
    return export_to_png(processed_image, output_path, dpi, optimize)


def export_to_svg(
    image: Image.Image,
    output_path: str | Path,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    pixel_size: int = 1,
) -> Path:
    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ExportError(
            f"Failed to create output directory: {output_path.parent}. Error: {e}"
        ) from e

    def parse_color(color):
        if isinstance(color, str):
            from PIL import ImageColor

            rgb = ImageColor.getrgb(color)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        if isinstance(color, tuple) and len(color) >= 3:
            return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        return str(color)

    bg_svg = parse_color(bg_color)
    fg_svg = parse_color(fg_color)
    width, height = image.size
    svg_width = width * pixel_size
    svg_height = height * pixel_size

    svg = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(svg_width),
            "height": str(svg_height),
            "viewBox": f"0 0 {svg_width} {svg_height}",
        },
    )
    ET.SubElement(
        svg,
        "rect",
        {
            "x": "0",
            "y": "0",
            "width": str(svg_width),
            "height": str(svg_height),
            "fill": bg_svg,
        },
    )
    fg_group = ET.SubElement(svg, "g", {"fill": fg_svg})

    if image.mode == "1":
        for y in range(height):
            for x in range(width):
                if image.getpixel((x, y)) == 0:
                    ET.SubElement(
                        fg_group,
                        "rect",
                        {
                            "x": str(x * pixel_size),
                            "y": str(y * pixel_size),
                            "width": str(pixel_size),
                            "height": str(pixel_size),
                        },
                    )
    elif image.mode == "L":
        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                if isinstance(pixel, int) and pixel < 128:
                    ET.SubElement(
                        fg_group,
                        "rect",
                        {
                            "x": str(x * pixel_size),
                            "y": str(y * pixel_size),
                            "width": str(pixel_size),
                            "height": str(pixel_size),
                        },
                    )
    else:
        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                if (
                    isinstance(pixel, tuple)
                    and len(pixel) >= 3
                    and pixel[:3] != (255, 255, 255)
                ):
                    ET.SubElement(
                        fg_group,
                        "rect",
                        {
                            "x": str(x * pixel_size),
                            "y": str(y * pixel_size),
                            "width": str(pixel_size),
                            "height": str(pixel_size),
                        },
                    )

    tree = ET.ElementTree(svg)
    try:
        tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
    except Exception as e:
        raise ExportError(f"Failed to save SVG file: {output_path}. Error: {e}") from e
    return output_path
