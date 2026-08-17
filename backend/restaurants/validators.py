"""
Reusable, storage-agnostic image validators.

These are applied at the model layer (field `validators=[...]`) so they run
on every save path — admin, DRF serializers, seed scripts, shell — not just
one entry point. They work against Django's `UploadedFile`/`FieldFile` API
only, so they keep working unchanged if the underlying storage backend is
later swapped for S3, Cloudinary, etc. (see storage.py).
"""
import os

from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_SIZE_MB = 5


def validate_image_extension(file) -> None:
    """Reject files whose extension isn't an allowed image format."""
    ext = os.path.splitext(getattr(file, "name", "") or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported image format '{ext or 'unknown'}'. "
            f"Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}."
        )


def validate_image_size(file) -> None:
    """Reject files above MAX_IMAGE_SIZE_MB."""
    max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    size = getattr(file, "size", None)
    if size is not None and size > max_bytes:
        raise ValidationError(f"Image file too large. Max size is {MAX_IMAGE_SIZE_MB}MB.")


def validate_image_integrity(file) -> None:
    """
    Reject files that merely *look* like images (right extension) but are
    corrupted or aren't actually decodable image data. Prevents corrupted
    media records from ever reaching storage.
    """
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        # Pillow isn't installed — skip the deep check rather than hard-fail
        # unrelated deployments. Extension/size validation still applies.
        return

    try:
        file.seek(0)
        with Image.open(file) as img:
            if img.format not in ALLOWED_PIL_FORMATS:
                raise ValidationError(
                    "Unsupported image content. Allowed formats: JPEG, PNG, WEBP."
                )
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("Uploaded file is not a valid image.") from exc
    finally:
        try:
            file.seek(0)
        except Exception:
            pass
