"""
Pillow-based image generator for note.com header images.
"""

import os
from PIL import Image, ImageDraw, ImageFont


# note.com recommended image size
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 670

# Background image path (user-provided, not tracked in git)
BACKGROUND_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "header_background.png"
)

# Fallback gradient colors (purple to blue) - used if no background image
GRADIENT_START = (102, 126, 234)  # #667eea
GRADIENT_END = (118, 75, 162)     # #764ba2

# Text settings
TEXT_COLOR = (0, 0, 0)  # Black


def create_header_image(date: str, output_path: str) -> str:
    """
    Create a header image with background and date text overlay.

    Uses a user-provided background image if available,
    otherwise falls back to a gradient background.

    Args:
        date: Date string in YYYY.MM.DD format
        output_path: Path to save the generated image

    Returns:
        Path to the generated image
    """
    # Load background (user image or gradient fallback)
    image = _load_background_image()

    # Add date text
    _add_date_text(image, date)

    # Save image
    image.save(output_path, "PNG", quality=95)
    return output_path


def _load_background_image() -> Image.Image:
    """
    Load the user-provided background image.
    Falls back to gradient if no image is found.
    """
    # Try multiple extensions
    for ext in [".png", ".jpg", ".jpeg"]:
        path = BACKGROUND_IMAGE_PATH.replace(".png", ext)
        if os.path.exists(path):
            print(f"Loading background image: {path}")
            img = Image.open(path).convert("RGB")
            # Resize to fit note.com's recommended size
            return img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    # Fallback to gradient
    print("No background image found, using gradient fallback")
    return _create_gradient_background()


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
    font = _get_font(size=180)

    # Main date text
    main_text = date

    # Center the text horizontally and position higher vertically
    # Using anchor="mm" (middle-middle) for precise centering
    center_x = IMAGE_WIDTH // 2
    center_y = int(IMAGE_HEIGHT * 0.40)  # Position text in upper-center area

    # Draw text centered (no shadow, black text only)
    draw.text((center_x, center_y), main_text, font=font, fill=TEXT_COLOR, anchor="mm")


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Get a font, with fallbacks for different environments."""
    # List of fonts to try (common on various systems)
    # Pacifico is prioritized as it's the preferred font
    font_paths = [
        # User-provided Pacifico font (in assets folder)
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "Pacifico-Regular.ttf"
        ),
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
                font = ImageFont.truetype(font_path, size)
                print(f"✓ Loaded font: {font_path}")
                return font
            except (OSError, IOError) as e:
                print(f"✗ Failed to load {font_path}: {e}")
                continue

    # Fall back to default font
    print("⚠ Using default font (Pacifico not found)")
    return ImageFont.load_default()


if __name__ == "__main__":
    # Test execution
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(output_dir, "assets", "test_header.png")

    create_header_image("2024.01.15", output_file)
    print(f"Generated: {output_file}")
