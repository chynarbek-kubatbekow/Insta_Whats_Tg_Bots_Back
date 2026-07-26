from __future__ import annotations

import logging
from typing import Any

import httpx

from app.bots.base import IncomingMessage
from app.core.config import Settings
from app.models.message import Channel

logger = logging.getLogger(__name__)


class InstagramBotClient:
    max_text_length = 1000

    def __init__(self, settings: Settings) -> None:
        self._access_token = settings.secret(settings.instagram_page_access_token)
        self._instagram_user_id = settings.instagram_user_id
        self._graph_api_version = settings.meta_graph_api_version

    async def send_text(self, chat_id: str, text: str) -> bool:
        if not self._access_token or not self._instagram_user_id:
            logger.warning("Instagram credentials are not configured; reply skipped")
            return False

        url = (
            f"https://graph.facebook.com/"
            f"{self._graph_api_version}/{self._instagram_user_id}/messages"
        )
        headers = {"Authorization": f"Bearer {self._access_token}"}
        payload = {
            "recipient": {"id": chat_id},
            "message": {"text": text},
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        return True


def parse_instagram_updates(payload: dict[str, Any]) -> list[IncomingMessage]:
    updates: list[IncomingMessage] = []

    if payload.get("object") not in {None, "instagram"}:
        return updates

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender = (event.get("sender") or {}).get("id")
            message = event.get("message") or {}
            postback = event.get("postback") or {}
            text = message.get("text") or postback.get("title") or postback.get("payload")

            is_own_message = (
                message.get("is_echo")
                or message.get("is_self")
                or event.get("is_echo")
                or event.get("is_self")
            )
            is_unavailable = message.get("is_deleted") or message.get("is_unsupported")

            if is_own_message or is_unavailable or not sender or not text:
                continue

            updates.append(
                IncomingMessage(
                    channel=Channel.INSTAGRAM,
                    external_chat_id=str(sender),
                    external_user_id=str(sender),
                    external_message_id=str(message.get("mid")) if message.get("mid") else None,
                    text=text,
                    raw_payload=event,
                )
            )

    return updates
