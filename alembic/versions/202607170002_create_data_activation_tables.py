from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision = "202607170002"
down_revision = "202607170001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "staged_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_user_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_staged_records_source", "staged_records", ["source"])
    op.create_index("ix_staged_records_status", "staged_records", ["status"])
    op.create_index("ix_staged_records_external_user_id", "staged_records", ["external_user_id"])
    op.create_index(
        "ix_staged_records_status_created",
        "staged_records",
        ["status", "created_at"],
    )

    op.create_table(
        "activated_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("staged_record_id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_user_id", sa.String(length=255), nullable=True),
        sa.Column("data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["staged_record_id"],
            ["staged_records.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("staged_record_id"),
    )
    op.create_index(
        "ix_activated_records_staged_record_id",
        "activated_records",
        ["staged_record_id"],
    )
    op.create_index("ix_activated_records_source", "activated_records", ["source"])
    op.create_index(
        "ix_activated_records_external_user_id",
        "activated_records",
        ["external_user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_activated_records_external_user_id", table_name="activated_records")
    op.drop_index("ix_activated_records_source", table_name="activated_records")
    op.drop_index("ix_activated_records_staged_record_id", table_name="activated_records")
    op.drop_table("activated_records")

    op.drop_index("ix_staged_records_status_created", table_name="staged_records")
    op.drop_index("ix_staged_records_external_user_id", table_name="staged_records")
    op.drop_index("ix_staged_records_status", table_name="staged_records")
    op.drop_index("ix_staged_records_source", table_name="staged_records")
    op.drop_table("staged_records")
