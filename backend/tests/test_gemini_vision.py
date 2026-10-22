"""Gemini provider tests. A fake client stands in for the SDK: no real API calls."""

import json
from types import SimpleNamespace

import httpx
import pytest
from google.genai import errors

from app.config import Settings
from app.errors import VisionServiceError
from app.services.vision import GeminiVisionProvider, create_vision_provider
from app.services.vision.prompt import USER_PROMPT, build_system_prompt

CATEGORIES = ["t-shirt", "jeans"]


class FakeClient:
    """Mimics client.models.generate_content: returns `text` or raises `error`."""

    def __init__(self, text: str | None = None, error: Exception | None = None) -> None:
        self.calls: list[dict] = []
        self._text = text
        self._error = error
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        return SimpleNamespace(text=self._text)


def provider_replying(text: str | None) -> tuple[GeminiVisionProvider, FakeClient]:
    client = FakeClient(text=text)
    return GeminiVisionProvider(model="test-model", client=client, categories=CATEGORIES), client


def test_valid_json_is_parsed_into_items():
    reply = {"items": [
        {"category": "Kurta", "material": "Cotton", "condition": "new", "confidence": 0.9, "label": "white kurta"},
        {"category": "jeans", "material": "cotton", "condition": "thrifted", "confidence": 0.8},
    ]}
    provider, _ = provider_replying(json.dumps(reply))

    items = provider.detect_items(b"img", "image/jpeg")

    assert [(i.category, i.material, i.condition, i.label) for i in items] == [
        ("kurta", "cotton", "new", "white kurta"),
        ("jeans", "cotton", "second-hand", None),
    ]


def test_no_clothing_gives_an_empty_list():
    provider, _ = provider_replying('{"items": []}')

    assert provider.detect_items(b"img", "image/png") == []


def test_invalid_item_is_skipped_and_the_rest_kept():
    provider, _ = provider_replying(json.dumps({"items": [{"material": "silk"}, {"category": "saree"}]}))

    assert [i.category for i in provider.detect_items(b"img", "image/jpeg")] == ["saree"]


@pytest.mark.parametrize(
    "text",
    [
        "not json at all",
        '{"items": [',               # cut off
        '{"clothes": []}',           # wrong key
        "",                          # empty answer
        None,                        # no text, e.g. a blocked answer
    ],
)
def test_bad_reply_raises_vision_service_error(text):
    provider, _ = provider_replying(text)

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"img", "image/jpeg")


REQUEST = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/test-model:generateContent")


@pytest.mark.parametrize(
    "error",
    [
        errors.ClientError(429, {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}}),
        errors.ClientError(400, {"error": {"code": 400, "message": "API key not valid", "status": "INVALID_ARGUMENT"}}),
        errors.ServerError(503, {"error": {"code": 503, "message": "overloaded", "status": "UNAVAILABLE"}}),
        httpx.ReadTimeout("timed out", request=REQUEST),
        httpx.ConnectError("no network", request=REQUEST),
    ],
)
def test_api_errors_and_timeouts_raise_vision_service_error(error):
    provider = GeminiVisionProvider(model="test-model", client=FakeClient(error=error))

    with pytest.raises(VisionServiceError) as caught:
        provider.detect_items(b"img", "image/jpeg")

    assert caught.value.__cause__ is error


def test_request_sends_image_shared_prompt_and_asks_for_json():
    provider, client = provider_replying('{"items": []}')

    provider.detect_items(b"\x89PNG bytes", "image/png")

    [call] = client.calls
    assert call["model"] == "test-model"
    image_part, text = call["contents"]
    assert (image_part.inline_data.data, image_part.inline_data.mime_type) == (b"\x89PNG bytes", "image/png")
    assert text == USER_PROMPT
    assert call["config"].system_instruction == build_system_prompt(CATEGORIES)
    assert call["config"].response_mime_type == "application/json"


def settings(**overrides) -> Settings:
    # _env_file=None: tests must not depend on the developer's real .env.
    return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize("key", [None, ""])
def test_gemini_without_api_key_raises_a_clear_error(key):
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        create_vision_provider(settings(vision_provider="gemini", gemini_api_key=key), CATEGORIES)


def test_factory_builds_gemini_provider_with_a_key_and_the_configured_model():
    # Creating the SDK client makes no network call.
    provider = create_vision_provider(
        settings(vision_provider="gemini", gemini_api_key="test-key", gemini_model="gemini-custom"), CATEGORIES
    )

    assert isinstance(provider, GeminiVisionProvider)
    assert provider.name == "gemini"
    assert provider._model == "gemini-custom"


def test_default_model_is_a_gemini_flash_model(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    assert "flash" in settings().gemini_model


# Debugging: the real reason must reach the log, never the key or the image.

@pytest.mark.parametrize("text", ['```json\n{"items": [{"category": "jeans"}]}\n```', '```\n{"items": [{"category": "jeans"}]}\n```'])
def test_json_in_a_code_fence_is_parsed(text):
    provider, _ = provider_replying(text)

    assert [i.category for i in provider.detect_items(b"img", "image/jpeg")] == ["jeans"]


def test_api_error_is_logged_with_its_type_and_message_but_not_the_key(caplog):
    caplog.set_level("WARNING", logger="uvicorn.error")
    error = errors.ClientError(400, {"error": {"code": 400, "message": "API key not valid. key=AIza-secret", "status": "INVALID_ARGUMENT"}})
    provider = GeminiVisionProvider(model="m", api_key="AIza-secret", client=FakeClient(error=error))

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"\x89PNG secret-image-bytes", "image/png")

    assert "Gemini request failed: ClientError: 400 INVALID_ARGUMENT" in caplog.text
    assert "API key not valid" in caplog.text
    assert "AIza-secret" not in caplog.text
    assert "secret-image-bytes" not in caplog.text


def test_timeout_is_logged(caplog):
    caplog.set_level("WARNING", logger="uvicorn.error")
    provider = GeminiVisionProvider(model="m", client=FakeClient(error=httpx.ReadTimeout("timed out", request=REQUEST)))

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"img", "image/jpeg")

    assert "Gemini request failed: ReadTimeout: timed out" in caplog.text


@pytest.mark.parametrize("response, reason", [
    (SimpleNamespace(text=None, prompt_feedback=SimpleNamespace(block_reason="SAFETY"), candidates=None), "blocked: SAFETY"),
    (SimpleNamespace(text=None, prompt_feedback=None, candidates=[SimpleNamespace(finish_reason="MAX_TOKENS")]), "finish reason: MAX_TOKENS"),
    (SimpleNamespace(text=None), "no candidates"),
])
def test_empty_answer_logs_why(caplog, response, reason):
    caplog.set_level("WARNING", logger="uvicorn.error")
    client = FakeClient()
    client.models.generate_content = lambda **kwargs: response
    provider = GeminiVisionProvider(model="m", client=client)

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"img", "image/jpeg")

    assert f"Gemini returned no text ({reason})" in caplog.text


def test_unreadable_answer_is_logged(caplog):
    caplog.set_level("WARNING", logger="uvicorn.error")
    provider, _ = provider_replying("Sorry, I can't help with that.")

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"img", "image/jpeg")

    assert "Gemini returned an unreadable answer: \"Sorry, I can't help with that.\"" in caplog.text
