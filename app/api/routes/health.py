from __future__ import annotations

from fastapi import APIRouter, Response, status

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.head("/health", include_in_schema=False)
async def health_check_head() -> Response:
    return Response(status_code=status.HTTP_200_OK)
