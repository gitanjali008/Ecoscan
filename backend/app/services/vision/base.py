from typing import Protocol

from app.schemas import DetectedItem


class VisionProvider(Protocol):
    """Anything that can recognise clothing items in an image.

    Image validation (type, size, empty file) happens before this is called,
    so providers can assume they get real image bytes.
    """

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]: ...
