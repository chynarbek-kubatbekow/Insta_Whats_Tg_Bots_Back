from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.models.message import Channel


@dataclass(slots=True)
class IncomingMessage:
    channel: Channel
    external_chat_id: str
    text: str
    external_user_id: str | None = None
    external_message_id: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)
    is_greeting_trigger: bool = False


class BotClient(Protocol):
    max_text_length: int

    async def send_text(self, chat_id: str, text: str) -> bool:
        """Send text to a channel chat. Returns False when credentials are not configured."""
