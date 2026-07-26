from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StagedRecordStatus(StrEnum):
    DRAFT = "draft"
    ACTIVATED = "activated"


class StagedRecord(Base):
    __tablename__ = "staged_records"
    __table_args__ = (Index("ix_staged_records_status_created", "status", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source: Mapped[str] = mapped_column(String(64), default="api", index=True)
    external_user_id: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[StagedRecordStatus] = mapped_column(
        Enum(
            StagedRecordStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
        ),
        default=StagedRecordStatus.DRAFT,
        index=True,
    )
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    activated_record: Mapped[ActivatedRecord | None] = relationship(
        back_populates="staged_record",
        cascade="all, delete-orphan",
    )


class ActivatedRecord(Base):
    __tablename__ = "activated_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    staged_record_id: Mapped[str] = mapped_column(
        ForeignKey("staged_records.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(64), index=True)
    external_user_id: Mapped[str | None] = mapped_column(String(255), index=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    staged_record: Mapped[StagedRecord] = relationship(back_populates="activated_record")
