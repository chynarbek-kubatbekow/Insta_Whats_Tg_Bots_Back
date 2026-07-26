from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import DbSession
from app.core.config import get_settings
from app.models.data_record import StagedRecordStatus
from app.repositories.data_record_repository import DataRecordRepository
from app.schemas.data_records import (
    ActivatedRecordRead,
    StagedRecordCreate,
    StagedRecordRead,
)

router = APIRouter(prefix="/api/v1/staged-records", tags=["data-records"])


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    settings = get_settings()
    expected_key = settings.secret(settings.api_key)
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


ApiKey = Annotated[None, Depends(require_api_key)]


@router.post("", response_model=StagedRecordRead, status_code=status.HTTP_201_CREATED)
async def create_staged_record(
    payload: StagedRecordCreate,
    session: DbSession,
    _: ApiKey,
) -> StagedRecordRead:
    repository = DataRecordRepository(session)
    record = await repository.create_staged(
        source=payload.source,
        external_user_id=payload.external_user_id,
        data=payload.data,
    )
    await session.commit()
    await session.refresh(record)
    return StagedRecordRead.model_validate(record)


@router.get("", response_model=list[StagedRecordRead])
async def list_staged_records(
    session: DbSession,
    _: ApiKey,
    status_filter: StagedRecordStatus | None = None,
    limit: int = 100,
) -> list[StagedRecordRead]:
    repository = DataRecordRepository(session)
    records = await repository.list_staged(status=status_filter, limit=min(limit, 500))
    return [StagedRecordRead.model_validate(record) for record in records]


@router.post("/{record_id}/activate", response_model=ActivatedRecordRead)
async def activate_staged_record(
    record_id: str,
    session: DbSession,
    _: ApiKey,
) -> ActivatedRecordRead:
    repository = DataRecordRepository(session)
    staged_record = await repository.get_staged_for_update(record_id)
    if staged_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    activated_record = await repository.activate(staged_record)
    await session.commit()
    await session.refresh(activated_record)
    return ActivatedRecordRead.model_validate(activated_record)
