from app.config import Settings


def test_default_image_limit_is_10_mb(monkeypatch):
    # The browser already sends small JPEGs; this limit is only a safety net.
    monkeypatch.delenv("MAX_IMAGE_MB", raising=False)
    settings = Settings(_env_file=None)

    assert settings.max_image_mb == 10
    assert settings.max_image_bytes == 10 * 1024 * 1024


def test_image_limit_can_be_set_from_the_environment(monkeypatch):
    monkeypatch.setenv("MAX_IMAGE_MB", "2.5")

    assert Settings(_env_file=None).max_image_bytes == int(2.5 * 1024 * 1024)
