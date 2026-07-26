from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.data_record import ActivatedRecord, StagedRecord, StagedRecordStatus


class DataRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_staged(
        self,
        *,
        source: str,
        data: dict,
        external_user_id: str | None = None,
    ) -> StagedRecord:
        record = StagedRecord(
            source=source,
            external_user_id=external_user_id,
            data=data,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def list_staged(
        self,
        *,
        status: StagedRecordStatus | None = None,
        limit: int = 100,
    ) -> list[StagedRecord]:
        statement = select(StagedRecord).order_by(StagedRecord.created_at.desc()).limit(limit)
        if status is not None:
            statement = statement.where(StagedRecord.status == status)

        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def get_staged_for_update(self, record_id: str) -> StagedRecord | None:
        statement = (
            select(StagedRecord)
            .where(StagedRecord.id == record_id)
            .options(selectinload(StagedRecord.activated_record))
            .with_for_update()
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def activate(self, staged_record: StagedRecord) -> ActivatedRecord:
        if staged_record.activated_record is not None:
            return staged_record.activated_record

        activated = ActivatedRecord(
            staged_record_id=staged_record.id,
            source=staged_record.source,
            external_user_id=staged_record.external_user_id,
            data=staged_record.data,
        )
        staged_record.status = StagedRecordStatus.ACTIVATED
        staged_record.activated_at = datetime.now(UTC)

        self._session.add(activated)
        await self._session.flush()
        return activated
