"""Checks an uploaded file before it is sent to a vision provider.

The declared content type comes from the client and can lie, so the file's
first bytes (its "magic number") are checked too: a .txt renamed to .jpg fails.
"""

from app.errors import EmptyImageError, ImageTooLargeError, InvalidImageError

# Kept here, next to the signature checks, so every allowed type can be verified.
ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")

# Non-standard names some clients send for an allowed type.
_TYPE_ALIASES = {"image/jpg": "image/jpeg", "image/pjpeg": "image/jpeg"}


def detect_image_type(data: bytes) -> str | None:
    """The real image type from the file's first bytes, or None if not allowed."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_image(data: bytes, content_type: str | None, max_bytes: int) -> str:
    """Raise if the upload is not a usable image; otherwise return its real type."""
    declared = (content_type or "").split(";")[0].strip().lower()
    declared = _TYPE_ALIASES.get(declared, declared)
    if declared not in ALLOWED_IMAGE_TYPES:
        raise InvalidImageError(f"Unsupported file type '{content_type}'. Upload a JPEG, PNG or WebP image.")

    if not data:
        raise EmptyImageError()

    if len(data) > max_bytes:
        raise ImageTooLargeError(f"The image is too large. The limit is {max_bytes / (1024 * 1024):g} MB.")

    actual = detect_image_type(data)
    if actual is None:
        raise InvalidImageError("The file is not a valid JPEG, PNG or WebP image.")
    return actual
