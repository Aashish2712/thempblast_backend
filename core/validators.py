from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image


MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100 MB

MIN_IMAGE_WIDTH = 800
MIN_IMAGE_HEIGHT = 450


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
}
def validate_article_image(file):
    if not file:
        return

    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "Image size must not exceed 10 MB."
        )

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            "Allowed image formats are JPG, JPEG, PNG and WebP."
        )

    try:
        image = Image.open(file)
        width, height = image.size

    except Exception:
        raise ValidationError(
            "The uploaded file is not a valid image."
        )

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        raise ValidationError(
            "Image must be at least 800 × 450 pixels."
        )

    try:
        image.verify()
    except Exception:
        raise ValidationError(
            "The uploaded image appears to be corrupted."
        )
def validate_article_video(file):
    if not file:
        return

    if file.size > MAX_VIDEO_SIZE:
        raise ValidationError(
            "Video size must not exceed 100 MB."
        )

    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            "Allowed video formats are MP4, WebM and MOV."
        )
