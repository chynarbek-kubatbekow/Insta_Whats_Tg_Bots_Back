from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "202607170001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("channel", sa.String(length=32), nullable=False, index=True),
        sa.Column("external_chat_id", sa.String(length=255), nullable=False, index=True),
        sa.Column("external_user_id", sa.String(length=255), nullable=True, index=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_conversation_channel_chat_created",
        "conversation_messages",
        ["channel", "external_chat_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversation_channel_chat_created", table_name="conversation_messages")
    op.drop_table("conversation_messages")
