from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.bots.base import BotClient, IncomingMessage
from app.core.config import Settings, get_settings
from app.models.message import MessageRole
from app.repositories.club_repository import ClubRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.messages import DispatchResult
from app.services.ai_service import AIService


class MessageDispatcher:
    def __init__(
        self,
        bot_client: BotClient,
        ai_service: AIService | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._bot_client = bot_client
        self._settings = settings or get_settings()
        self._ai_service = ai_service or AIService()

    async def handle_incoming(
        self,
        incoming: IncomingMessage,
        session: AsyncSession,
    ) -> DispatchResult:
        repository = MessageRepository(session)
        if await repository.was_processed(
            channel=incoming.channel,
            external_message_id=incoming.external_message_id,
        ):
            return DispatchResult(reply_text="", reply_sent=False, duplicate=True)

        previous_history = await repository.recent_for_chat(
            channel=incoming.channel,
            external_chat_id=incoming.external_chat_id,
            limit=1,
        )

        await repository.add(
            channel=incoming.channel,
            external_chat_id=incoming.external_chat_id,
            external_user_id=incoming.external_user_id,
            external_message_id=incoming.external_message_id,
            role=MessageRole.USER,
            text=incoming.text,
            payload=incoming.raw_payload,
        )

        normalized_text = incoming.text.strip().casefold()
        greetings = {"hi", "hello", "hey", "привет", "здравствуйте", "салам", "сәлем"}
        if incoming.is_greeting_trigger or (not previous_history and normalized_text in greetings):
            reply_text = self._settings.bot_initial_greeting
        else:
            knowledge_context = await ClubRepository(session).knowledge_context()
            reply_text = await self._ai_service.generate_grounded_reply(
                incoming.text,
                knowledge_context,
                self._settings.bot_unknown_answer,
            )

        max_length = max(1, self._bot_client.max_text_length)
        chunks = [reply_text[i : i + max_length] for i in range(0, len(reply_text), max_length)]
        sent_results = [
            await self._bot_client.send_text(incoming.external_chat_id, chunk) for chunk in chunks
        ]
        reply_sent = all(sent_results)

        await repository.add(
            channel=incoming.channel,
            external_chat_id=incoming.external_chat_id,
            external_user_id=incoming.external_user_id,
            role=MessageRole.ASSISTANT,
            text=reply_text,
            payload={"sent": reply_sent},
        )
        await session.commit()

        return DispatchResult(reply_text=reply_text, reply_sent=reply_sent)
