"""Centralized backend settings loaded from environment variables and .env."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Backend configuration."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str | None = None
    OPENAI_TIMEOUT_SECONDS: float = 120.0

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


def get_settings() -> Settings:
    """Return the settings instance managed by the application injector."""
    from .di import injector

    return cast(Settings, injector.get(Settings))
