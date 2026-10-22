"""The prompt and reply parsing shared by every real vision provider.

Keeping them in one place means each provider asks the same question and checks
the answer the same way. Giving the model the known categories makes it pick
names the carbon table recognises, instead of falling back to the default footprint.
"""

import logging
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ValidationError

from app.errors import VisionServiceError
from app.schemas import DetectedItem

logger = logging.getLogger(__name__)

USER_PROMPT = "List every clothing item, footwear and accessory in this image."

_TEMPLATE = """You identify clothing in photos for a carbon footprint app.
Reply with ONLY a JSON object, no other text, in exactly this shape:
{{"items": [{{"category": "dress", "material": "polyester", "condition": "new", "confidence": 0.9, "label": "red floral midi dress"}}]}}
Rules:
- Detect EVERY item of clothing, footwear and accessory that is visible (e.g. bag, belt, scarf, cap), one entry per item. If two similar items are visible, list both. Ignore people, furniture and everything else.
- category: one of the known categories below when it fits. Otherwise a short generic name in lowercase.
- material: your best guess of the main fabric or material in lowercase, e.g. "cotton", "organic cotton", "polyester", "wool", "leather". Use "unknown" if you cannot tell.
- condition: exactly "new" or "second-hand". Use "second-hand" only if there are visible signs of wear (fading, pilling, stretched or worn areas) or the photo looks like a thrift or vintage listing. Otherwise use "new".
- confidence: a number from 0 to 1 for how sure you are about the item.
- label: a short description a person would recognise, e.g. "red floral midi dress", "white canvas sneakers".
- If there is no clothing, footwear or accessory in the image, reply {{"items": []}}.
Known categories: {categories}"""


def build_system_prompt(categories: Iterable[str]) -> str:
    """The system prompt, listing the categories the carbon table knows."""
    return _TEMPLATE.format(categories=", ".join(categories) or "(none)")


class _VisionReply(BaseModel):
    """Outer shape of the model's reply. Items are checked one by one later."""

    items: list[Any]


def parse_items(content: str) -> list[DetectedItem]:
    """Turn the model's JSON reply into items, skipping any item that is invalid."""
    try:
        reply = _VisionReply.model_validate_json(content)
    except ValidationError as exc:
        raise VisionServiceError("The image recognition service returned an unreadable answer.") from exc

    items = []
    for raw in reply.items:
        try:
            items.append(DetectedItem.model_validate(raw))
        except ValidationError:
            # One odd item should not fail the whole scan.
            logger.warning("Skipping invalid item from vision model: %r", raw)
    return items
