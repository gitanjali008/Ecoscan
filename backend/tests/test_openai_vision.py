"""OpenAI provider tests. A fake client stands in for the SDK: no real API calls."""

import base64
import json
from types import SimpleNamespace

import httpx
import openai
import pytest

from app.config import Settings
from app.errors import VisionServiceError
from app.services.vision import (
    PROVIDERS,
    MockVisionProvider,
    OpenAIVisionProvider,
    create_vision_provider,
)
from app.services.vision.prompt import USER_PROMPT, build_system_prompt

CATEGORIES = ["t-shirt", "jeans"]


class FakeClient:
    """Mimics client.chat.completions.create: returns `content` or raises `error`."""

    def __init__(self, content: str | None = None, error: Exception | None = None) -> None:
        self.calls: list[dict] = []
        self._content = content
        self._error = error
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def provider_replying(content: str | None, categories=()) -> tuple[OpenAIVisionProvider, FakeClient]:
    client = FakeClient(content=content)
    return OpenAIVisionProvider(model="test-model", client=client, categories=categories), client


def test_valid_json_is_parsed_into_items():
    reply = {"items": [
        {"category": "T-Shirt", "material": "Organic Cotton", "condition": "new", "confidence": 0.9},
        {"category": "jeans", "material": "cotton", "condition": "used", "confidence": 0.8},
    ]}
    provider, _ = provider_replying(json.dumps(reply))

    items = provider.detect_items(b"img", "image/jpeg")

    assert [(i.category, i.material, i.condition) for i in items] == [
        ("t-shirt", "organic cotton", "new"),
        ("jeans", "cotton", "second-hand"),
    ]


def test_label_is_kept():
    reply = {"items": [{"category": "dress", "label": " red floral midi dress "}]}
    provider, _ = provider_replying(json.dumps(reply))

    [item] = provider.detect_items(b"img", "image/jpeg")

    assert item.label == "red floral midi dress"


def test_missing_fields_get_defaults():
    provider, _ = provider_replying('{"items": [{"category": "hat"}]}')

    [item] = provider.detect_items(b"img", "image/png")

    assert (item.material, item.condition, item.confidence, item.label) == ("unknown", "new", 1.0, None)


def test_no_clothing_gives_an_empty_list():
    provider, _ = provider_replying('{"items": []}')

    assert provider.detect_items(b"img", "image/png") == []


@pytest.mark.parametrize(
    "bad_item",
    [
        {"material": "cotton"},                         # no category
        {"category": ""},                               # empty category
        {"category": "jeans", "condition": "broken"},   # unknown condition
        {"category": "jeans", "confidence": 7},         # confidence above 1
        "jeans",                                        # not an object
    ],
)
def test_invalid_item_is_skipped_and_the_rest_kept(bad_item):
    provider, _ = provider_replying(json.dumps({"items": [bad_item, {"category": "jacket"}]}))

    items = provider.detect_items(b"img", "image/jpeg")

    assert [i.category for i in items] == ["jacket"]


@pytest.mark.parametrize(
    "content",
    [
        "not json at all",
        '{"items": [',               # cut off
        '["t-shirt"]',               # not an object
        '{"clothes": []}',           # wrong key
        '{"items": "t-shirt"}',      # items is not a list
        "",                          # empty answer
        None,                        # no content (e.g. a refusal)
    ],
)
def test_bad_reply_raises_vision_service_error(content):
    provider, _ = provider_replying(content)

    with pytest.raises(VisionServiceError):
        provider.detect_items(b"img", "image/jpeg")


REQUEST = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


@pytest.mark.parametrize(
    "error",
    [
        openai.APITimeoutError(request=REQUEST),
        openai.APIConnectionError(request=REQUEST),
        openai.RateLimitError("slow down", response=httpx.Response(429, request=REQUEST), body=None),
        openai.OpenAIError("anything else from the SDK"),
    ],
)
def test_api_errors_raise_vision_service_error(error):
    provider = OpenAIVisionProvider(model="test-model", client=FakeClient(error=error))

    with pytest.raises(VisionServiceError) as caught:
        provider.detect_items(b"img", "image/jpeg")

    assert caught.value.__cause__ is error


def test_request_sends_model_json_mode_and_base64_image():
    provider, client = provider_replying('{"items": []}')

    provider.detect_items(b"\x89PNG bytes", "image/png")

    [call] = client.calls
    assert call["model"] == "test-model"
    assert call["response_format"] == {"type": "json_object"}
    assert call["messages"][1]["content"][0]["text"] == USER_PROMPT
    image_part = call["messages"][1]["content"][1]
    expected = "data:image/png;base64," + base64.b64encode(b"\x89PNG bytes").decode()
    assert image_part["image_url"]["url"] == expected


def test_request_uses_the_shared_prompt_with_the_known_categories():
    provider, client = provider_replying('{"items": []}', categories=["saree", "jeans"])

    provider.detect_items(b"img", "image/jpeg")

    [call] = client.calls
    assert call["messages"][0] == {"role": "system", "content": build_system_prompt(["saree", "jeans"])}


def settings(**overrides) -> Settings:
    # _env_file=None: tests must not depend on the developer's real .env.
    return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize("key", [None, ""])
def test_openai_without_api_key_raises_a_clear_error(key):
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        create_vision_provider(settings(vision_provider="openai", openai_api_key=key), CATEGORIES)


def test_factory_builds_openai_provider_with_a_key():
    # Creating the SDK client makes no network call.
    provider = create_vision_provider(settings(vision_provider="openai", openai_api_key="sk-test"), CATEGORIES)

    assert isinstance(provider, OpenAIVisionProvider)
    assert "Known categories: t-shirt, jeans" in provider._system_prompt


def test_factory_builds_mock_provider():
    provider = create_vision_provider(settings(vision_provider="mock", openai_api_key=None), CATEGORIES)

    assert isinstance(provider, MockVisionProvider)


def test_both_providers_are_registered():
    assert set(PROVIDERS) == {"mock", "openai"}
