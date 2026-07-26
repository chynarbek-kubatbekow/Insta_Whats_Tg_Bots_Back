from __future__ import annotations

import hashlib
import hmac

import pytest

from app.core.config import Settings
from app.core.security import verify_meta_signature
from app.services.ai_service import STRICT_SYSTEM_PROMPT, AIService


def test_postgres_url_is_normalized_for_asyncpg() -> None:
    settings = Settings(
        database_url=(
            "postgresql://user:password@host/database?sslmode=require&channel_binding=require"
        )
    )
    assert settings.database_url == (
        "postgresql+asyncpg://user:password@host/database?ssl=require"
    )


def test_meta_signature() -> None:
    body = b'{"object":"whatsapp_business_account"}'
    secret = "app-secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_meta_signature(body, f"sha256={digest}", secret)
    assert not verify_meta_signature(body, "sha256=invalid", secret)


@pytest.mark.asyncio
async def test_ai_without_key_returns_safe_fallback() -> None:
    service = AIService(Settings(GROQ_API_KEY="replace-me"))
    answer = await service.generate_grounded_reply(
        "Придумай расписание",
        "Набор начинается 15 сентября.",
        "Пока не знаю.",
    )
    assert answer == "Пока не знаю."


def test_ai_prompt_allows_general_beauty_questions_but_protects_salon_facts() -> None:
    assert "общие вопросы по теме салона красоты" in STRICT_SYSTEM_PROMPT
    assert "ТОЛЬКО фактами из БАЗЫ ЗНАНИЙ" in STRICT_SYSTEM_PROMPT
    assert "Не ставь диагнозы" in STRICT_SYSTEM_PROMPT
