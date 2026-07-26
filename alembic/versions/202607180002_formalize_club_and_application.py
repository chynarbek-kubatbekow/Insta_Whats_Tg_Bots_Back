from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "202607180002"
down_revision = "202607180001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


FORMAL_KNOWLEDGE_TITLES = [
    "Официальный статус и назначение клуба",
    "Кто может подать заявку",
    "Порядок рассмотрения заявки",
    "Общие правила поведения участников",
    "Требования к тренировкам и безопасности",
    "Правила обработки данных заявки",
    "Основания для отказа или исключения",
]


def upgrade() -> None:
    op.add_column(
        "club_applications",
        sa.Column("faculty", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "club_applications",
        sa.Column("contact", sa.String(length=255), nullable=True),
    )
    op.execute(
        "UPDATE club_applications "
        "SET faculty = study_info, contact = phone "
        "WHERE faculty IS NULL OR contact IS NULL"
    )
    op.alter_column("club_applications", "faculty", nullable=False)
    op.alter_column("club_applications", "contact", nullable=False)
    op.drop_column("club_applications", "comment")
    op.drop_column("club_applications", "study_info")
    op.drop_column("club_applications", "phone")

    knowledge_entries = sa.table(
        "knowledge_entries",
        sa.column("title", sa.String()),
        sa.column("content", sa.Text()),
        sa.column("category", sa.String()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        knowledge_entries,
        [
            {
                "title": "Официальный статус и назначение клуба",
                "category": "rules",
                "content": (
                    "Баскетбольный клуб IT-Лицея-99 является добровольным студенческим "
                    "спортивным объединением. Цель клуба — регулярные тренировки, развитие "
                    "игровых навыков, командной дисциплины и участие в спортивных мероприятиях."
                ),
                "is_active": True,
            },
            {
                "title": "Кто может подать заявку",
                "category": "rules",
                "content": (
                    "Заявку может подать действующий студент IT-Лицея-99 независимо от факультета "
                    "и курса. В заявке необходимо указать настоящее ФИО, факультет и действующий "
                    "контакт для связи. Отправка заявки не означает автоматическое зачисление "
                    "в клуб."
                ),
                "is_active": True,
            },
            {
                "title": "Порядок рассмотрения заявки",
                "category": "rules",
                "content": (
                    "После отправки заявка поступает администраторам клуба. Представитель клуба "
                    "связывается с кандидатом по указанному WhatsApp номеру или Telegram username. "
                    "Решение о приёме сообщается индивидуально. Заявки принимаются без ограничения "
                    "по времени, начиная с 15 сентября."
                ),
                "is_active": True,
            },
            {
                "title": "Общие правила поведения участников",
                "category": "rules",
                "content": (
                    "Участник обязан соблюдать уважительное общение, командную дисциплину и "
                    "организационные решения капитана и вице-капитана. Оскорбления, дискриминация, "
                    "агрессивное поведение и намеренное создание конфликтов не допускаются. "
                    "О невозможности посетить тренировку следует сообщать заранее."
                ),
                "is_active": True,
            },
            {
                "title": "Требования к тренировкам и безопасности",
                "category": "rules",
                "content": (
                    "На тренировку необходимо приходить вовремя, в спортивной форме и подходящей "
                    "обуви. Участник обязан выполнять требования безопасности и сообщить капитану "
                    "об ограничениях здоровья, которые могут повлиять на тренировку. При плохом "
                    "самочувствии участнику следует воздержаться от физической нагрузки."
                ),
                "is_active": True,
            },
            {
                "title": "Правила обработки данных заявки",
                "category": "rules",
                "content": (
                    "ФИО, факультет, WhatsApp номер и Telegram username используются только для "
                    "рассмотрения заявки и связи с кандидатом. Доступ к заявкам имеют "
                    "администраторы клуба. Для исправления или удаления данных кандидат может "
                    "обратиться к капитану или вице-капитану по контактам клуба."
                ),
                "is_active": True,
            },
            {
                "title": "Основания для отказа или исключения",
                "category": "rules",
                "content": (
                    "Основанием для отказа в приёме или прекращения участия могут быть ложные "
                    "данные в заявке, отсутствие связи с кандидатом, систематическое нарушение "
                    "дисциплины, небезопасное поведение, неуважение к участникам или игнорирование "
                    "правил клуба."
                ),
                "is_active": True,
            },
        ],
    )

    op.execute(
        "UPDATE bot_settings SET value = "
        "'Официальный информационный бот баскетбольного клуба IT-Лицея-99.\n\n"
        "Здесь можно получить информацию о клубе и подать заявку на вступление.' "
        "WHERE key = 'welcome_message'"
    )
    op.execute(
        "UPDATE bot_settings SET value = "
        "'Заявка принята и передана администраторам клуба. Представитель клуба свяжется с вами "
        "по указанному контакту. Информация о первой тренировке будет опубликована в общей группе "
        "после приёма участников.' WHERE key = 'application_success_text'"
    )


def downgrade() -> None:
    titles = ", ".join(f"'{title}'" for title in FORMAL_KNOWLEDGE_TITLES)
    op.execute(f"DELETE FROM knowledge_entries WHERE title IN ({titles})")

    op.add_column(
        "club_applications",
        sa.Column("phone", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "club_applications",
        sa.Column("study_info", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "club_applications",
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
    )
    op.execute(
        "UPDATE club_applications SET phone = contact, study_info = faculty "
        "WHERE phone IS NULL OR study_info IS NULL"
    )
    op.alter_column("club_applications", "phone", nullable=False)
    op.alter_column("club_applications", "study_info", nullable=False)
    op.drop_column("club_applications", "contact")
    op.drop_column("club_applications", "faculty")
