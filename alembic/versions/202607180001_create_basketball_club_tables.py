from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "202607180001"
down_revision = "202607170002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    knowledge_entries = op.create_table(
        "knowledge_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False, server_default="general"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_knowledge_entries_category", "knowledge_entries", ["category"])
    op.create_index("ix_knowledge_entries_is_active", "knowledge_entries", ["is_active"])

    op.create_table(
        "club_applications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("telegram_user_id", sa.String(length=32), nullable=False),
        sa.Column("telegram_chat_id", sa.String(length=32), nullable=False),
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("study_info", sa.String(length=255), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_club_applications_telegram_user_id", "club_applications", ["telegram_user_id"]
    )
    op.create_index(
        "ix_club_applications_telegram_chat_id", "club_applications", ["telegram_chat_id"]
    )
    op.create_index("ix_club_applications_status", "club_applications", ["status"])

    op.create_table(
        "telegram_states",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    bot_settings = op.create_table(
        "bot_settings",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "admin_change_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_id", sa.String(length=32), nullable=False),
        sa.Column("admin_name", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("entity", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("details", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_admin_change_logs_admin_id", "admin_change_logs", ["admin_id"])

    op.bulk_insert(
        knowledge_entries,
        [
            {
                "title": "О клубе и сроках набора",
                "category": "recruitment",
                "content": (
                    "Это баскетбольный клуб IT-Лицея-99. Набор начинается 15 сентября. "
                    "Заявки принимаются без ограничения по времени."
                ),
                "is_active": True,
            },
            {
                "title": "Капитан команды",
                "category": "contacts",
                "content": (
                    "Капитан команды — Кубтабек уулу Чнырабек, студент 2 курса, "
                    "группа Бр-1-2/25. Телефон: +996 509 200 945. Telegram: @chinasbek."
                ),
                "is_active": True,
            },
            {
                "title": "Вице-капитан команды",
                "category": "contacts",
                "content": (
                    "Вице-капитан команды — Айдаров Керимек Жаркынбекович. "
                    "Телефон: +996 505 414 149. Telegram: @PdafBYxvL."
                ),
                "is_active": True,
            },
            {
                "title": "Как вступить в клуб",
                "category": "recruitment",
                "content": (
                    "Чтобы узнать о наборе, можно подать заявку в этом Telegram-боте или написать "
                    "капитану @chinasbek либо вице-капитану @PdafBYxvL."
                ),
                "is_active": True,
            },
            {
                "title": "Первая тренировка и объявления",
                "category": "training",
                "content": (
                    "Дата, время и место первой тренировки, а также все дальнейшие объявления "
                    "будут опубликованы в общей Telegram-группе. Группу создадут после приёма "
                    "участников."
                ),
                "is_active": True,
            },
        ],
    )

    op.bulk_insert(
        bot_settings,
        [
            {
                "key": "welcome_message",
                "title": "Приветственное сообщение",
                "value": (
                    "Официальный информационный бот баскетбольного клуба IT-Лицея-99.\n\n"
                    "Здесь можно получить информацию о клубе и подать заявку на вступление."
                ),
            },
            {
                "key": "application_success_text",
                "title": "Текст после заявки",
                "value": (
                    "Заявка принята! Администраторы получили её. Информацию о первой тренировке "
                    "объявят в общей группе, которую создадут после приёма участников."
                ),
            },
            {
                "key": "unknown_answer",
                "title": "Ответ при отсутствии информации",
                "value": (
                    "Пока не знаю ответа на этот вопрос. Напишите капитану @chinasbek "
                    "или вице-капитану @PdafBYxvL."
                ),
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_admin_change_logs_admin_id", table_name="admin_change_logs")
    op.drop_table("admin_change_logs")
    op.drop_table("bot_settings")
    op.drop_table("telegram_states")
    op.drop_index("ix_club_applications_status", table_name="club_applications")
    op.drop_index("ix_club_applications_telegram_chat_id", table_name="club_applications")
    op.drop_index("ix_club_applications_telegram_user_id", table_name="club_applications")
    op.drop_table("club_applications")
    op.drop_index("ix_knowledge_entries_is_active", table_name="knowledge_entries")
    op.drop_index("ix_knowledge_entries_category", table_name="knowledge_entries")
    op.drop_table("knowledge_entries")
