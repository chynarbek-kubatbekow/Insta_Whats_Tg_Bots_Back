from __future__ import annotations

from pydantic import BaseModel


class DispatchResult(BaseModel):
    reply_text: str
    reply_sent: bool
    duplicate: bool = False
