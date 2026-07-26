from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Aruu Beauty Meta Bot"
    environment: str = "development"
    debug: bool = False
    app_public_url: str = "http://localhost:8000"
    bot_initial_greeting: str = (
        "Здравствуйте! Вы написали в Aruu Beauty ✨ "
        "Я помогу узнать об услугах и ценах, мастерах, графике и правилах записи. "
        "Что вас интересует?"
    )
    bot_unknown_answer: str = (
        "Не хочу давать неточную информацию. Напишите «администратор», "
        "и сотрудник Aruu Beauty поможет вам."
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bot_backend"

    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_temperature: float = 0.1
    groq_max_completion_tokens: int = 1024
    groq_top_p: float = 1
    groq_reasoning_effort: str | None = "low"
    groq_disable_ssl_verify: bool = False

    meta_graph_api_version: str = "v23.0"
    whatsapp_access_token: SecretStr | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_app_secret: SecretStr | None = None

    instagram_page_access_token: SecretStr | None = None
    instagram_user_id: str | None = None
    instagram_verify_token: SecretStr | None = None
    instagram_app_secret: SecretStr | None = None

    api_key: SecretStr = Field(default=SecretStr("change-this"))
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            value = value.replace("postgres://", "postgresql+asyncpg://", 1)
        elif value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)

        parsed = urlsplit(value)
        query_items = parse_qsl(parsed.query, keep_blank_values=True)
        normalized_query: list[tuple[str, str]] = []
        ssl_mode: str | None = None
        for key, item_value in query_items:
            if key == "sslmode":
                ssl_mode = item_value
            elif key != "channel_binding":
                normalized_query.append((key, item_value))
        if ssl_mode and not any(key == "ssl" for key, _ in normalized_query):
            normalized_query.append(("ssl", ssl_mode))

        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                urlencode(normalized_query),
                parsed.fragment,
            )
        )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> bool:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @staticmethod
    def secret(value: SecretStr | None) -> str | None:
        if value is None:
            return None
        secret = value.get_secret_value()
        if not secret or secret == "replace-me":
            return None
        return secret


@lru_cache
def get_settings() -> Settings:
    return Settings()
