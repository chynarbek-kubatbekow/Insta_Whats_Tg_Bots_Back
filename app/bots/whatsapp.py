from __future__ import annotations

import logging
from typing import Any

import httpx

from app.bots.base import IncomingMessage
from app.core.config import Settings
from app.models.message import Channel

logger = logging.getLogger(__name__)


class WhatsAppBotClient:
    max_text_length = 4096

    def __init__(self, settings: Settings) -> None:
        self._access_token = settings.secret(settings.whatsapp_access_token)
        self._phone_number_id = settings.whatsapp_phone_number_id
        self._graph_api_version = settings.meta_graph_api_version

    async def send_text(self, chat_id: str, text: str) -> bool:
        if not self._access_token or not self._phone_number_id:
            logger.warning("WhatsApp credentials are not configured; reply skipped")
            return False

        url = (
            f"https://graph.facebook.com/{self._graph_api_version}/{self._phone_number_id}/messages"
        )
        headers = {"Authorization": f"Bearer {self._access_token}"}
        payload = {
            "messaging_product": "whatsapp",
            "to": chat_id,
            "type": "text",
            "text": {"body": text},
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        return True


def parse_whatsapp_updates(payload: dict[str, Any]) -> list[IncomingMessage]:
    updates: list[IncomingMessage] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") not in {None, "messages"}:
                continue
            value = change.get("value", {})
            for message in value.get("messages", []):
                interactive = message.get("interactive") or {}
                text = (
                    (message.get("text") or {}).get("body")
                    or (message.get("button") or {}).get("text")
                    or (interactive.get("button_reply") or {}).get("title")
                    or (interactive.get("list_reply") or {}).get("title")
                )
                sender = message.get("from")
                if not text or not sender:
                    continue

                updates.append(
                    IncomingMessage(
                        channel=Channel.WHATSAPP,
                        external_chat_id=str(sender),
                        external_user_id=str(sender),
                        external_message_id=(
                            str(message.get("id")) if message.get("id") else None
                        ),
                        text=text,
                        raw_payload=message,
                    )
                )

    return updates
