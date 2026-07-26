from __future__ import annotations

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Channel, ConversationMessage, MessageRole


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        channel: Channel,
        external_chat_id: str,
        role: MessageRole,
        text: str,
        external_user_id: str | None = None,
        external_message_id: str | None = None,
        payload: dict | None = None,
    ) -> ConversationMessage:
        message = ConversationMessage(
            channel=channel,
            external_chat_id=external_chat_id,
            external_user_id=external_user_id,
            external_message_id=external_message_id,
            role=role,
            text=text,
            payload=payload or {},
        )
        self._session.add(message)
        await self._session.flush()
        return message

    async def was_processed(self, *, channel: Channel, external_message_id: str | None) -> bool:
        if not external_message_id:
            return False
        statement = select(
            exists().where(
                ConversationMessage.channel == channel,
                ConversationMessage.external_message_id == external_message_id,
                ConversationMessage.role == MessageRole.USER,
            )
        )
        return bool((await self._session.execute(statement)).scalar_one())

    async def recent_for_chat(
        self,
        *,
        channel: Channel,
        external_chat_id: str,
        limit: int = 12,
    ) -> list[ConversationMessage]:
        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.channel == channel,
                ConversationMessage.external_chat_id == external_chat_id,
            )
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return list(reversed(result.scalars().all()))
