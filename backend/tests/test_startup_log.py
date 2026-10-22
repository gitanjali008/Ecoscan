"""The startup log says which vision provider is active, and never shows a key."""

import pytest

from app.config import Settings
from app.main import log_vision_provider

SECRET = "AIzaSy-very-secret-test-key"


def logged(caplog, **settings) -> str:
    caplog.set_level("INFO", logger="uvicorn.error")
    log_vision_provider(Settings(_env_file=None, **settings))
    return caplog.text


def test_logs_the_active_provider_and_model(caplog):
    text = logged(caplog, vision_provider="gemini", gemini_api_key=SECRET, gemini_model="gemini-test")

    assert "Vision provider: gemini (model gemini-test)" in text
    assert "API_KEY is empty" not in text


def test_mock_is_logged_as_sample_results(caplog):
    assert "Vision provider: mock, sample results only" in logged(caplog, vision_provider="mock")


@pytest.mark.parametrize("provider, key_field", [("gemini", "gemini_api_key"), ("openai", "openai_api_key")])
def test_never_logs_the_key(caplog, provider, key_field):
    assert SECRET not in logged(caplog, vision_provider=provider, **{key_field: SECRET})


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_warns_when_the_key_is_missing(caplog, provider):
    text = logged(caplog, vision_provider=provider)

    assert f"VISION_PROVIDER={provider} but {provider.upper()}_API_KEY is empty" in text
