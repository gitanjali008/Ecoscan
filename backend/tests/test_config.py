from app.config import ENV_FILE, Settings


def test_default_image_limit_is_10_mb(monkeypatch):
    # The browser already sends small JPEGs; this limit is only a safety net.
    monkeypatch.delenv("MAX_IMAGE_MB", raising=False)
    settings = Settings(_env_file=None)

    assert settings.max_image_mb == 10
    assert settings.max_image_bytes == 10 * 1024 * 1024


def test_image_limit_can_be_set_from_the_environment(monkeypatch):
    monkeypatch.setenv("MAX_IMAGE_MB", "2.5")

    assert Settings(_env_file=None).max_image_bytes == int(2.5 * 1024 * 1024)


def test_env_file_is_backend_env_whatever_the_working_directory():
    assert ENV_FILE.is_absolute()
    assert ENV_FILE.name == ".env"
    assert (ENV_FILE.parent / "app" / "config.py").is_file()  # i.e. the backend/ folder
    assert Settings.model_config["env_file"] == ENV_FILE


def test_settings_ignore_a_dot_env_in_the_working_directory(tmp_path, monkeypatch):
    # backend/.env says gemini; uvicorn is started from another folder that has its own .env.
    backend_env = tmp_path / "backend" / ".env"
    backend_env.parent.mkdir()
    backend_env.write_text("VISION_PROVIDER=gemini\nGEMINI_API_KEY=test-key\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / ".env").write_text("VISION_PROVIDER=openai\n")
    monkeypatch.chdir(elsewhere)
    for name in ("VISION_PROVIDER", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setitem(Settings.model_config, "env_file", backend_env)

    settings = Settings()

    assert settings.vision_provider == "gemini"
    assert settings.gemini_api_key == "test-key"
