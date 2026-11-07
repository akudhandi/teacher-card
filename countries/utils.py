"""
Utility functions shared across all countries
"""

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from pathlib import Path
import os
import random
import re
import warnings

# Default banner text stamped on demo/test documents.
DEFAULT_WATERMARK_TEXT = "SAMPLE - NOT A VALID DOCUMENT"


def load_font(size_or_name, size=None, bold: bool = False) -> ImageFont.FreeTypeFont:
    """
    Load font with cross-platform support (Linux/Windows)
    
    Supports both old and new signature:
    - Old: load_font('arial', 24) or load_font('arialbd', 24)
    - New: load_font(24, bold=True) or load_font(24)
    
    Args:
        size_or_name: Font size (int) or font name (str) for backward compatibility
        size: Font size when first arg is font name (backward compatibility)
        bold: Whether to use bold font (default: False)
        
    Returns:
        ImageFont object
    """
    # Detect old vs new signature
    if isinstance(size_or_name, str):
        # Old signature: load_font('arial', 24)
        font_name = size_or_name
        font_size = size if size is not None else 24
        # Determine if bold based on font name
        is_bold = 'bd' in font_name.lower() or 'bold' in font_name.lower()
    else:
        # New signature: load_font(24, bold=True)
        font_size = size_or_name
        is_bold = bold
    
    # Bundled fonts (package data) — deterministic across all OSes
    bundled_dir = Path(__file__).parent / "fonts"
    bundled_bold = bundled_dir / "DejaVuSans-Bold.ttf"
    bundled_regular = bundled_dir / "DejaVuSans.ttf"

    # Font paths based on bold (bundled first, then system fonts)
    if is_bold:
        font_paths = [
            str(bundled_bold),
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/Arial-Bold.ttf',
            'arialbd.ttf'
        ]
    else:
        font_paths = [
            str(bundled_regular),
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            'C:/Windows/Fonts/arial.ttf',
            'arial.ttf'
        ]
    
    # Try each path
    for path in font_paths:
        try:
            return ImageFont.truetype(path, font_size)
        except:
            continue
    
    # Ultimate fallback
    warnings.warn(
        "load_font: no TrueType font found on this system; falling back to the "
        "built-in bitmap font. Text layout and sizing will differ from the "
        "bundled DejaVu Sans.",
        RuntimeWarning,
        stacklevel=2,
    )
    return ImageFont.load_default()


# Global cache for photos per session (name-based)
_PHOTO_CACHE = {}

# Optional explicit photo file for the person currently being rendered.
_ACTIVE_PHOTO_PATH = None


def set_active_photo(path):
    """Set (or clear with None) an explicit photo file for the next render."""
    global _ACTIVE_PHOTO_PATH
    _ACTIVE_PHOTO_PATH = str(path) if path else None


def validate_dob(dob: str) -> str:
    """Validate a display date-of-birth string.

    The exact date format varies per country, so this only enforces that a
    value is present and contains a four-digit year. Raises ValueError otherwise.
    """
    value = (dob or "").strip()
    if not value:
        raise ValueError("date_of_birth is required.")
    if not re.search(r"\b(1[89]\d{2}|20\d{2})\b", value):
        raise ValueError(
            f"date_of_birth '{dob}' must contain a four-digit year (e.g. 12/05/1988)."
        )
    return value

def get_profile_photo(size: tuple = (280, 340), person_id: str = None, gender: str = "Random") -> Image.Image:
    """
    Load a profile photo from foto folder
    Falls back to generated avatar if no photos found
    
    Args:
        size: Tuple of (width, height)
        person_id: Optional identifier for person (e.g., "john_doe") to cache photo
        gender: Gender filter - "Male", "Female", or "Random" (default)
    
    Returns:
        PIL Image or None
    """
    # Check cache first if person_id provided
    if person_id and person_id in _PHOTO_CACHE:
        cached_photo = _PHOTO_CACHE[person_id]
        if cached_photo:
            return cached_photo.resize(size, Image.Resampling.LANCZOS)
        return None

    # Explicit per-person photo file takes priority over the bundled pool.
    if _ACTIVE_PHOTO_PATH and Path(_ACTIVE_PHOTO_PATH).is_file():
        try:
            photo = Image.open(_ACTIVE_PHOTO_PATH)
            if photo.mode != "RGB":
                photo = photo.convert("RGB")
            if person_id:
                _PHOTO_CACHE[person_id] = photo.copy()
            return photo.resize(size, Image.Resampling.LANCZOS)
        except Exception:
            pass

    try:
        # Foto directory: override via YOWES_FOTO_DIR, else bundled with the package
        foto_dir = Path(os.environ.get("YOWES_FOTO_DIR", "")) if os.environ.get("YOWES_FOTO_DIR") else Path(__file__).parent / "foto"
        
        if foto_dir.exists() and foto_dir.is_dir():
            # Get all image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            all_photos = [f for f in foto_dir.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
            
            # Filter by gender prefix if specified
            if gender == "Male":
                photos = [p for p in all_photos if p.stem.startswith('p')]
            elif gender == "Female":
                photos = [p for p in all_photos if p.stem.startswith('w')]
            else:  # Random
                photos = all_photos
            
            if photos:
                # Random select a photo (use hash of person_id for consistency)
                if person_id:
                    # Use hash to consistently select same photo for same person
                    photo_index = hash(person_id) % len(photos)
                    selected_photo = photos[photo_index]
                else:
                    selected_photo = random.choice(photos)
                    
                photo = Image.open(selected_photo)
                
                # Convert to RGB if needed (for PNG with alpha)
                if photo.mode != 'RGB':
                    photo = photo.convert('RGB')
                
                # Cache the photo if person_id provided
                if person_id:
                    _PHOTO_CACHE[person_id] = photo.copy()
                
                # Resize to requested size
                photo = photo.resize(size, Image.Resampling.LANCZOS)
                return photo
    except Exception as e:
        pass
    
    # Cache None if person_id provided and no photo found
    if person_id:
        _PHOTO_CACHE[person_id] = None
    
    # Fallback: return None to indicate no photo available
    return None

def clear_photo_cache():
    """Clear the photo cache (call at start of new generation session)"""
    global _PHOTO_CACHE
    _PHOTO_CACHE.clear()


def generate_initials_avatar(first: str, last: str, size: tuple = (280, 340), 
                             bg_color: tuple = (70, 130, 180)) -> Image.Image:
    """Generate simple avatar with initials as fallback"""
    photo = Image.new('RGB', size, bg_color)
    
    try:
        from PIL import ImageDraw
        draw = ImageDraw.Draw(photo)
        
        font = load_font('arial', 72)
        
        initials = f"{first[0]}{last[0]}"
        draw.text((size[0]//2, size[1]//2), initials, fill=(255, 255, 255), font=font, anchor="mm")
    except:
        pass
    
    return photo


def apply_watermark(
    image: Image.Image,
    text: str = DEFAULT_WATERMARK_TEXT,
    angle: int = 30,
    opacity: int = 60,
    color: tuple = (200, 0, 0),
) -> Image.Image:
    """Stamp a repeating diagonal banner across an image.

    Used to clearly mark demo/test output as non-authentic. Tiles `text` across
    the whole canvas at a fixed angle, then composites it over a copy of the
    source so the original is never mutated in place.
    """
    original_mode = image.mode
    base = image.convert("RGBA")
    w, h = base.size

    font_size = max(20, int(min(w, h) * 0.045))
    font = load_font(font_size, bold=True)
    text = text or DEFAULT_WATERMARK_TEXT

    bbox = font.getbbox(text)
    text_w = max(1, bbox[2] - bbox[0])
    text_h = max(1, bbox[3] - bbox[1])

    # Build one tile large enough that a rotated copy still covers the canvas seam.
    tile_w = text_w + font_size * 6
    tile_h = max(text_h * 3, int(text_h * 2.5))
    tile = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 0))
    tile_draw = ImageDraw.Draw(tile)
    row_step = max(text_h * 2, font_size * 3)
    for row_y in range(0, tile_h, row_step):
        tile_draw.text((font_size, row_y), text, font=font, fill=(*color, opacity))

    tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    tile_w, tile_h = tile.size

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for x in range(-tile_w, w + tile_w, tile_w):
        for y in range(-tile_h, h + tile_h, tile_h):
            layer.alpha_composite(tile, (x, y))

    merged = Image.alpha_composite(base, layer)
    return merged.convert(original_mode if original_mode != "P" else "RGB")


def finalize_document(
    data: bytes,
    watermark: bool = True,
    text: str = DEFAULT_WATERMARK_TEXT,
) -> bytes:
    """Apply optional watermarking to encoded PNG bytes and re-encode to PNG."""
    if not watermark:
        return data
    with Image.open(BytesIO(data)) as img:
        img.load()
        stamped = apply_watermark(img, text=text)
    buffer = BytesIO()
    stamped.save(buffer, format="PNG")
    return buffer.getvalue()


# Encodable output formats -> file extension and PIL format name.
SUPPORTED_FORMATS = {
    "png": (".png", "PNG"),
    "jpg": (".jpg", "JPEG"),
    "jpeg": (".jpg", "JPEG"),
    "pdf": (".pdf", "PDF"),
}


def normalize_format(fmt: str) -> str:
    """Lowercase + validate an output format, defaulting to png."""
    fmt = (fmt or "png").strip().lower().lstrip(".")
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {sorted(set(SUPPORTED_FORMATS))}"
        )
    return fmt


def format_extension(fmt: str) -> str:
    """Return the file extension (with dot) for a given output format."""
    return SUPPORTED_FORMATS[normalize_format(fmt)][0]


def encode_document(data: bytes, fmt: str = "png", quality: int = 90, dpi: int = 300) -> bytes:
    """Re-encode rendered PNG bytes into png/jpg/pdf.

    Args:
        data: PNG bytes as produced by a country's generate_document.
        fmt: Target format ('png', 'jpg', or 'pdf').
        quality: JPEG quality (1-100), ignored for other formats.
        dpi: Resolution embedded in PDF output; controls the page's physical size.
    """
    fmt = normalize_format(fmt)
    if fmt == "png":
        return data

    pil_format = SUPPORTED_FORMATS[fmt][1]
    with Image.open(BytesIO(data)) as img:
        img.load()
        buffer = BytesIO()
        if pil_format == "JPEG":
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(buffer, format="JPEG", quality=quality)
        elif pil_format == "PDF":
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(buffer, format="PDF", resolution=dpi)
        else:
            img.save(buffer, format=pil_format)
    return buffer.getvalue()
