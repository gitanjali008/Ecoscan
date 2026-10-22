"""Builds the vision provider named by VISION_PROVIDER in the settings.

Adding a provider means writing one class and adding one entry to PROVIDERS.
Each builder gets the settings and the known categories (for the shared prompt).
"""

from collections.abc import Callable, Sequence

from app.config import Settings
from app.services.vision.base import VisionProvider
from app.services.vision.mock import MockVisionProvider
from app.services.vision.openai_provider import OpenAIVisionProvider


def _openai(settings: Settings, categories: Sequence[str]) -> VisionProvider:
    return OpenAIVisionProvider(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        categories=categories,
    )


PROVIDERS: dict[str, Callable[[Settings, Sequence[str]], VisionProvider]] = {
    "mock": lambda settings, categories: MockVisionProvider(),
    "openai": _openai,
}


def create_vision_provider(settings: Settings, categories: Sequence[str]) -> VisionProvider:
    try:
        build = PROVIDERS[settings.vision_provider]
    except KeyError:
        raise ValueError(f"Unknown VISION_PROVIDER: {settings.vision_provider!r}") from None
    return build(settings, categories)
