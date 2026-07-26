"""Replace Telegram-specific storage with Meta channel storage."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "202607260001"
down_revision = "202607180003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversation_messages",
        sa.Column("external_message_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_conversation_messages_external_message_id",
        "conversation_messages",
        ["external_message_id"],
    )
    op.create_index(
        "uq_conversation_channel_external_message",
        "conversation_messages",
        ["channel", "external_message_id"],
        unique=True,
        postgresql_where=sa.text("external_message_id IS NOT NULL"),
    )
    op.add_column(
        "club_applications",
        sa.Column("channel", sa.String(length=32), nullable=False, server_default="whatsapp"),
    )
    op.drop_index("ix_club_applications_telegram_user_id", table_name="club_applications")
    op.drop_index("ix_club_applications_telegram_chat_id", table_name="club_applications")
    op.alter_column(
        "club_applications",
        "telegram_user_id",
        new_column_name="external_user_id",
        existing_type=sa.String(length=32),
        type_=sa.String(length=255),
    )
    op.alter_column(
        "club_applications",
        "telegram_chat_id",
        new_column_name="external_chat_id",
        existing_type=sa.String(length=32),
        type_=sa.String(length=255),
    )
    op.drop_column("club_applications", "telegram_username")
    op.create_index("ix_club_applications_channel", "club_applications", ["channel"])
    op.create_index(
        "ix_club_applications_external_user_id",
        "club_applications",
        ["external_user_id"],
    )
    op.create_index(
        "ix_club_applications_external_chat_id",
        "club_applications",
        ["external_chat_id"],
    )
    op.drop_table("telegram_states")


def downgrade() -> None:
    op.create_table(
        "telegram_states",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_index("ix_club_applications_external_user_id", table_name="club_applications")
    op.drop_index("ix_club_applications_external_chat_id", table_name="club_applications")
    op.drop_index("ix_club_applications_channel", table_name="club_applications")
    op.add_column(
        "club_applications",
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
    )
    op.alter_column(
        "club_applications",
        "external_chat_id",
        new_column_name="telegram_chat_id",
        existing_type=sa.String(length=255),
        type_=sa.String(length=32),
    )
    op.create_index(
        "ix_club_applications_telegram_user_id",
        "club_applications",
        ["telegram_user_id"],
    )
    op.create_index(
        "ix_club_applications_telegram_chat_id",
        "club_applications",
        ["telegram_chat_id"],
    )
    op.alter_column(
        "club_applications",
        "external_user_id",
        new_column_name="telegram_user_id",
        existing_type=sa.String(length=255),
        type_=sa.String(length=32),
    )
    op.drop_column("club_applications", "channel")
    op.drop_index("uq_conversation_channel_external_message", table_name="conversation_messages")
    op.drop_index(
        "ix_conversation_messages_external_message_id",
        table_name="conversation_messages",
    )
    op.drop_column("conversation_messages", "external_message_id")
