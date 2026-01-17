"""
Pillow-based image generator for note.com header images.
"""

import os
from PIL import Image, ImageDraw, ImageFont


# note.com recommended image size
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 670

# Gradient colors (purple to blue)
GRADIENT_START = (102, 126, 234)  # #667eea
GRADIENT_END = (118, 75, 162)     # #764ba2

# Text settings
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 80)


def create_header_image(date: str, output_path: str) -> str:
    """
    Create a header image with gradient background and date text.

    Args:
        date: Date string in YYYY.MM.DD format
        output_path: Path to save the generated image

    Returns:
        Path to the generated image
    """
    # Create gradient background
    image = _create_gradient_background()

    # Add date text
    _add_date_text(image, date)

    # Save image
    image.save(output_path, "PNG", quality=95)
    return output_path


def _create_gradient_background() -> Image.Image:
    """Create a gradient background image."""
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(image)

    for y in range(IMAGE_HEIGHT):
        # Calculate gradient ratio
        ratio = y / IMAGE_HEIGHT

        # Interpolate colors
        r = int(GRADIENT_START[0] + (GRADIENT_END[0] - GRADIENT_START[0]) * ratio)
        g = int(GRADIENT_START[1] + (GRADIENT_END[1] - GRADIENT_START[1]) * ratio)
        b = int(GRADIENT_START[2] + (GRADIENT_END[2] - GRADIENT_START[2]) * ratio)

        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b))

    return image


def _add_date_text(image: Image.Image, date: str) -> None:
    """Add date text to the center of the image."""
    draw = ImageDraw.Draw(image)

    # Try to load a nice font, fall back to default if not available
    font = _get_font(size=120)
    sub_font = _get_font(size=40)

    # Main date text
    main_text = date

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), main_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (IMAGE_WIDTH - text_width) // 2
    y = (IMAGE_HEIGHT - text_height) // 2 - 30

    # Draw shadow
    shadow_offset = 3
    draw.text(
        (x + shadow_offset, y + shadow_offset),
        main_text,
        font=font,
        fill=(0, 0, 0, 100)
    )

    # Draw main text
    draw.text((x, y), main_text, font=font, fill=TEXT_COLOR)

    # Add "Daily Log" subtitle
    subtitle = "Daily Log"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (IMAGE_WIDTH - sub_width) // 2
    sub_y = y + text_height + 20

    draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=(255, 255, 255, 200))


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Get a font, with fallbacks for different environments."""
    # List of fonts to try (common on various systems)
    font_paths = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
        # Linux (GitHub Actions)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue

    # Fall back to default font
    return ImageFont.load_default()


if __name__ == "__main__":
    # Test execution
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(output_dir, "assets", "test_header.png")

    create_header_image("2024.01.15", output_file)
    print(f"Generated: {output_file}")
