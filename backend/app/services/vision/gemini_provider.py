"""A vision provider backed by a Google Gemini model (works on the free tier).

It sends the same shared prompt as the OpenAI provider and asks for JSON output.
The reply is checked with Pydantic, so a bad answer becomes a VisionServiceError
instead of reaching the scoring code.
"""

from collections.abc import Sequence

import httpx
from google import genai
from google.genai import errors, types

from app.errors import VisionServiceError
from app.schemas import DetectedItem
from app.services.vision.prompt import USER_PROMPT, build_system_prompt, parse_items


class GeminiVisionProvider:
    """VisionProvider that asks a Gemini model to list clothing items."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        client: genai.Client | None = None,
        timeout: float = 30,
        categories: Sequence[str] = (),
    ) -> None:
        if client is None:
            if not api_key:
                raise ValueError("GEMINI_API_KEY is required when VISION_PROVIDER=gemini")
            # The SDK takes the timeout in milliseconds.
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=int(timeout * 1000)))
        self._client = client
        self._model = model
        self._config = types.GenerateContentConfig(
            system_instruction=build_system_prompt(categories),
            response_mime_type="application/json",
        )

    def detect_items(self, image: bytes, content_type: str) -> list[DetectedItem]:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[types.Part.from_bytes(data=image, mime_type=content_type), USER_PROMPT],
                config=self._config,
            )
        # APIError covers HTTP errors (quota, bad key, server errors); httpx raises timeouts and connection errors.
        except (errors.APIError, httpx.HTTPError) as exc:
            raise VisionServiceError() from exc

        # text is None when the model returned no text, e.g. a blocked answer.
        content = response.text
        if not content:
            raise VisionServiceError("The image recognition service returned an empty answer.")

        return parse_items(content)
