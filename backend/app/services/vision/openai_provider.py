"""A vision provider backed by an OpenAI vision model.

The model is asked for strict JSON and its reply is checked with Pydantic, so a
bad answer becomes a VisionServiceError instead of reaching the scoring code.
"""

import base64
from collections.abc import Sequence

from openai import OpenAI, OpenAIError

from app.errors import VisionServiceError
from app.schemas import DetectedItem
from app.services.vision.prompt import USER_PROMPT, build_system_prompt, parse_items


class OpenAIVisionProvider:
    """VisionProvider that asks an OpenAI vision model to list clothing items."""

    name = "openai"

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        client: OpenAI | None = None,
        timeout: float = 30,
        categories: Sequence[str] = (),
    ) -> None:
        if client is None:
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when VISION_PROVIDER=openai")
            client = OpenAI(api_key=api_key, timeout=timeout)
        self._client = client
        self._model = model
        self._system_prompt = build_system_prompt(categories)

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]:
        data_url = f"data:{content_type};base64,{base64.b64encode(image).decode('ascii')}"

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self._system_prompt},
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
