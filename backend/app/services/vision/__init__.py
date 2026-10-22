"""Vision: turns an image into a list of detected clothing items.

Callers depend only on the VisionProvider protocol, so the mock used for local
development and tests can be swapped for a real model without other changes.
"""

from app.services.vision.base import VisionProvider
from app.services.vision.factory import PROVIDERS, create_vision_provider
from app.services.vision.gemini_provider import GeminiVisionProvider
from app.services.vision.mock import MockVisionProvider
from app.services.vision.openai_provider import OpenAIVisionProvider

__all__ = [
    "VisionProvider",
    "MockVisionProvider",
    "OpenAIVisionProvider",
    "GeminiVisionProvider",
    "PROVIDERS",
    "create_vision_provider",
]
