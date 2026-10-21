"""A vision provider backed by an OpenAI vision model.

The model is asked for strict JSON and its reply is checked with Pydantic, so a
bad answer becomes a VisionServiceError instead of reaching the scoring code.
"""

import base64
import logging
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.errors import VisionServiceError
from app.schemas import DetectedItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You identify clothing in photos for a carbon footprint app.
Reply with ONLY a JSON object, no other text, in exactly this shape:
{"items": [{"category": "t-shirt", "material": "organic cotton", "condition": "new", "confidence": 0.9}]}
Rules:
- One entry per visible item of clothing, footwear or accessory (e.g. hat, bag, belt, scarf). Ignore everything else.
- category: a short common name in lowercase, e.g. "t-shirt", "jeans", "sneakers".
- material: your best guess of the main fabric in lowercase, or "unknown".
- condition: exactly "new" or "second-hand". Use "second-hand" only if the item clearly looks worn or vintage.
- confidence: a number from 0 to 1.
- If there is no clothing in the image, reply {"items": []}."""

USER_PROMPT = "List the clothing items in this image."


class _VisionReply(BaseModel):
    """Outer shape of the model's reply. Items are checked one by one later."""

    items: list[Any]


class OpenAIVisionProvider:
    """VisionProvider that asks an OpenAI vision model to list clothing items."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        client: OpenAI | None = None,
        timeout: float = 30,
    ) -> None:
        if client is None:
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when VISION_PROVIDER=openai")
            client = OpenAI(api_key=api_key, timeout=timeout)
        self._client = client
        self._model = model

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]:
        data_url = f"data:{content_type};base64,{base64.b64encode(image).decode('ascii')}"

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": USER_PROMPT},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    },
                ],
            )
        except OpenAIError as exc:  # also covers timeouts, connection and HTTP errors
            raise VisionServiceError() from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise VisionServiceError("The image recognition service returned an empty answer.")

        return parse_items(content)


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
