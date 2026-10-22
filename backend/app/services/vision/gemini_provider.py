"""A vision provider backed by a Google Gemini model (works on the free tier).

It sends the same shared prompt as the OpenAI provider and asks for JSON output.
The reply is checked with Pydantic, so a bad answer becomes a VisionServiceError
instead of reaching the scoring code.
"""

import logging
from collections.abc import Sequence

import httpx
from google import genai
from google.genai import errors, types

from app.errors import VisionServiceError
from app.schemas import DetectedItem
from app.services.vision.prompt import USER_PROMPT, build_system_prompt, parse_items

# Shown in the uvicorn terminal (see app/main.py). Never log the key or the image.
logger = logging.getLogger("uvicorn.error")


class GeminiVisionProvider:
    """VisionProvider that asks a Gemini model to list clothing items."""

    name = "gemini"

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
        self._api_key = api_key  # only to keep it out of logs
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
            # e.g. "ClientError: 400 INVALID_ARGUMENT ... API key not valid" or "ReadTimeout".
            logger.warning("Gemini request failed: %s: %s", type(exc).__name__, self._redact(str(exc))[:500])
            raise VisionServiceError() from exc

        # text is None when the model returned no text, e.g. a blocked answer.
        content = response.text
        if not content:
            logger.warning("Gemini returned no text (%s).", _why_empty(response))
            raise VisionServiceError("The image recognition service returned an empty answer.")

        try:
            return parse_items(content)
        except VisionServiceError:
            logger.warning("Gemini returned an unreadable answer: %r", content[:300])
            raise

    def _redact(self, text: str) -> str:
        """Error messages should not contain the key, but make sure."""
        return text.replace(self._api_key, "<redacted>") if self._api_key else text


def _why_empty(response) -> str:
    """The block or finish reason of an answer with no text, e.g. "blocked: SAFETY"."""
    feedback = getattr(response, "prompt_feedback", None)
    if feedback is not None and getattr(feedback, "block_reason", None):
        return f"blocked: {feedback.block_reason}"
    candidates = getattr(response, "candidates", None) or []
    if candidates and getattr(candidates[0], "finish_reason", None):
        return f"finish reason: {candidates[0].finish_reason}"
    return "no candidates"
