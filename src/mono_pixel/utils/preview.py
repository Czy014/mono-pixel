"""Preview and ASCII utilities extracted from CLI.

These are CLI-agnostic helpers for building terminal previews.
"""

from PIL import Image


def generate_ascii_preview(image: Image.Image, preview_width: int = 80) -> str:
    """Generate ASCII preview for terminal output."""
    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    preview_height = int(preview_width * aspect_ratio * 0.5)

    gray_image = image.convert("L").resize(
        (preview_width, preview_height), Image.Resampling.NEAREST
    )

    ascii_chars = " .:-=+*#%@"
    result = []

    for y in range(preview_height):
        line = []
        for x in range(preview_width):
            pixel = gray_image.getpixel((x, y))
            if isinstance(pixel, int):
                pixel_value = pixel
            elif isinstance(pixel, float):
                pixel_value = int(pixel)
            elif isinstance(pixel, tuple) and len(pixel) > 0:
                pixel_value = int(pixel[0])
            else:
                pixel_value = 255
            char_index = int(pixel_value / 255 * (len(ascii_chars) - 1))
            char_index = len(ascii_chars) - 1 - char_index
            line.append(ascii_chars[char_index])
        result.append("".join(line))

    return "\n".join(result)


def detect_content_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Detect content bounding box using top-left pixel as background reference."""
    rgb_image = image.convert("RGB")
    width, height = rgb_image.size
    bg_color = rgb_image.getpixel((0, 0))

    left = width
    top = height
    right = -1
    bottom = -1

    for y in range(height):
        for x in range(width):
            if rgb_image.getpixel((x, y)) != bg_color:
                if x < left:
                    left = x
                if y < top:
                    top = y
                if x > right:
                    right = x
                if y > bottom:
                    bottom = y

    if right < left or bottom < top:
        return None

    return (left, top, right, bottom)


def build_position_aware_preview(
    image: Image.Image,
    image_size: tuple[int, int],
    preview_width: int = 80,
) -> str:
    """Build an ASCII preview with frame and content bbox overlay."""
    original_width, original_height = image.size
    ascii_preview = generate_ascii_preview(image, preview_width)
    rows = ascii_preview.splitlines()

    if not rows:
        return f"Canvas: {image_size[0]}x{image_size[1]} px (empty preview)"

    preview_height = len(rows)
    grid = [list(row) for row in rows]

    content_bbox = detect_content_bbox(image)
    bbox_summary = "none"

    if content_bbox is not None:
        left, top, right, bottom = content_bbox
        x_scale = preview_width / original_width
        y_scale = preview_height / original_height

        p_left = max(0, min(preview_width - 1, int(left * x_scale)))
        p_top = max(0, min(preview_height - 1, int(top * y_scale)))
        p_right = max(0, min(preview_width - 1, int(right * x_scale)))
        p_bottom = max(0, min(preview_height - 1, int(bottom * y_scale)))

        for x in range(p_left, p_right + 1):
            grid[p_top][x] = "*"
            grid[p_bottom][x] = "*"
        for y in range(p_top, p_bottom + 1):
            grid[y][p_left] = "*"
            grid[y][p_right] = "*"

        bbox_summary = (
            f"({left},{top})-({right},{bottom}) px, "
            f"size={right - left + 1}x{bottom - top + 1}"
        )

    framed_rows: list[str] = ["+" + "-" * preview_width + "+"]
    for row in grid:
        framed_rows.append("|" + "".join(row) + "|")
    framed_rows.append("+" + "-" * preview_width + "+")

    header = [
        f"Canvas: {image_size[0]}x{image_size[1]} px",
        (
            f"Preview grid: {preview_width}x{preview_height} "
            f"(scale ~{image_size[0] / preview_width:.2f}px/col, "
            f"{image_size[1] / preview_height:.2f}px/row)"
        ),
        f"Detected text bbox: {bbox_summary}",
        "Legend: '*' indicates detected text bounding box",
    ]

    return "\n".join(header + [""] + framed_rows)
