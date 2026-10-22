from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/.env, found from this file. A plain ".env" is looked up in the folder
# uvicorn is started from, so starting it anywhere but backend/ silently ignored
# the file and fell back to the mock provider.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    app_name: str = "EcoScan API"
    vision_provider: Literal["mock", "openai", "gemini"] = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 30
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_timeout_seconds: float = 30
    max_image_mb: float = 10
    points_per_kg: float = 10
    cors_origins: str = "http://localhost:5173"

    @property
    def max_image_bytes(self) -> int:
        return int(self.max_image_mb * 1024 * 1024)


@lru_cache
def get_settings() -> Settings:
    return Settings()