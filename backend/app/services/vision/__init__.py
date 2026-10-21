"""Vision: turns an image into a list of detected clothing items.

Callers depend only on the VisionProvider protocol, so the mock used for local
development and tests can be swapped for a real model without other changes.
"""

from app.services.vision.base import VisionProvider
from app.services.vision.mock import MockVisionProvider

__all__ = ["VisionProvider", "MockVisionProvider"]
