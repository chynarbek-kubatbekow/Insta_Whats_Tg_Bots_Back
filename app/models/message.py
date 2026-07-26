from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Channel(StrEnum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index(
            "ix_conversation_channel_chat_created",
            "channel",
            "external_chat_id",
            "created_at",
        ),
        Index(
            "uq_conversation_channel_external_message",
            "channel",
            "external_message_id",
            unique=True,
            postgresql_where=text("external_message_id IS NOT NULL"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    channel: Mapped[Channel] = mapped_column(
        Enum(
            Channel,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
        ),
        index=True,
    )
    external_chat_id: Mapped[str] = mapped_column(String(255), index=True)
    external_user_id: Mapped[str | None] = mapped_column(String(255), index=True)
    external_message_id: Mapped[str | None] = mapped_column(String(255), index=True)
    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
        )
    )
    text: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
