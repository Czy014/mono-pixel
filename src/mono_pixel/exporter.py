"""Image export and binarization utilities."""

import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


class ExportError(Exception):
    """Raised when image export fails."""

    pass


def strict_binarization(
    image: Image.Image, threshold: int = 127, invert: bool = False
) -> Image.Image:
    """Strictly binarize image to pure black and white.

    Args:
        image: Input image.
        threshold: Binarization threshold in [0, 255].
        invert: Whether to invert output colors.

    Returns:
        Binarized 1-bit image.
    """
    if not (0 <= threshold <= 255):
        raise ValueError(f"Threshold must be in [0, 255], got: {threshold}")

    if image.mode != "L":
        gray_image = image.convert("L")
    else:
        gray_image = image

    width, height = gray_image.size
    binary_data = []

    for y in range(height):
        for x in range(width):
            pixel = gray_image.getpixel((x, y))
            pixel_value: int
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
    """Convert image to a two-color RGB image.

    Args:
        image: Input image.
        bg_color: Background color.
        fg_color: Foreground color.
        threshold: Binarization threshold.

    Returns:
        RGB two-color image.
    """
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
    """Export image to PNG file.

    Args:
        image: Image to export.
        output_path: Output file path.
        dpi: Output DPI.
        optimize: Whether to optimize PNG size.

    Returns:
        Path to output file.

    Raises:
        ExportError: Export failed.
    """
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
    """Run full image save pipeline.

    Args:
        image: Image to save.
        output_path: Output file path.
        strict_binarize: Whether to apply strict binarization.
        bg_color: Background color.
        fg_color: Foreground color.
        binarization_threshold: Binarization threshold.
        dpi: Output DPI (for PNG).
        optimize: Whether to optimize output size (for PNG).
        svg_pixel_size: Size of each pixel in SVG units (for SVG).

    Returns:
        Path to output file.
    """
    output_path = Path(output_path)

    if strict_binarize:
        processed_image = convert_to_monochrome(
            image, bg_color, fg_color, binarization_threshold
        )
    else:
        processed_image = image

    # Determine output format based on file extension
    suffix = output_path.suffix.lower()

    if suffix == ".svg":
        return export_to_svg(
            processed_image,
            output_path,
            bg_color=bg_color,
            fg_color=fg_color,
            pixel_size=svg_pixel_size,
        )
    else:
        # Default to PNG
        return export_to_png(processed_image, output_path, dpi, optimize)


def export_to_svg(
    image: Image.Image,
    output_path: str | Path,
    bg_color: str | tuple[int, int, int] = "white",
    fg_color: str | tuple[int, int, int] = "black",
    pixel_size: int = 1,
) -> Path:
    """Export image to SVG file.

    Args:
        image: Image to export (should be 1-bit or RGB).
        output_path: Output file path.
        bg_color: Background color.
        fg_color: Foreground color.
        pixel_size: Size of each pixel in SVG units.

    Returns:
        Path to output file.

    Raises:
        ExportError: Export failed.
    """
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
        elif isinstance(color, tuple) and len(color) >= 3:
            return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        return str(color)

    bg_svg = parse_color(bg_color)
    fg_svg = parse_color(fg_color)

    width, height = image.size
    svg_width = width * pixel_size
    svg_height = height * pixel_size

    # Create SVG root element
    svg = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(svg_width),
            "height": str(svg_height),
            "viewBox": f"0 0 {svg_width} {svg_height}",
        },
    )

    # Add background rectangle
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

    # Create a group for foreground pixels
    fg_group = ET.SubElement(svg, "g", {"fill": fg_svg})

    # Get pixel data based on image mode
    if image.mode == "1":
        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                # For 1-bit images, 0 is foreground (black)
                if pixel == 0:
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
                # For grayscale, treat dark pixels as foreground
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
        # RGB or RGBA
        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    # Treat non-white pixels as foreground
                    if pixel[:3] != (255, 255, 255):
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

    # Write SVG file
    tree = ET.ElementTree(svg)
    try:
        tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
    except Exception as e:
        raise ExportError(f"Failed to save SVG file: {output_path}. Error: {e}") from e

    return output_path
