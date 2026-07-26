from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.data_record import StagedRecordStatus


class StagedRecordCreate(BaseModel):
    source: str = Field(default="api", max_length=64)
    external_user_id: str | None = Field(default=None, max_length=255)
    data: dict[str, Any] = Field(default_factory=dict)


class StagedRecordRead(BaseModel):
    id: str
    source: str
    external_user_id: str | None
    status: StagedRecordStatus
    data: dict[str, Any]
    created_at: datetime
    activated_at: datetime | None

    model_config = {"from_attributes": True}


class ActivatedRecordRead(BaseModel):
    id: str
    staged_record_id: str
    source: str
    external_user_id: str | None
    data: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
