from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from app.api.dependencies import DbSession
from app.bots.whatsapp import WhatsAppBotClient, parse_whatsapp_updates
from app.core.config import get_settings
from app.core.security import verify_meta_signature
from app.services.message_dispatcher import MessageDispatcher

router = APIRouter(prefix="/webhooks", tags=["whatsapp"])


@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify_whatsapp_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> str:
    settings = get_settings()
    expected_token = settings.secret(settings.whatsapp_verify_token)

    if hub_mode == "subscribe" and expected_token and hub_verify_token == expected_token:
        return hub_challenge or ""

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid verify token")


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    session: DbSession,
) -> dict[str, object]:
    settings = get_settings()
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256")
    app_secret = settings.secret(settings.whatsapp_app_secret)

    if not app_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Meta app secret is not configured",
        )
    if not verify_meta_signature(body, signature, app_secret):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Meta signature")

    payload = await request.json()
    updates = parse_whatsapp_updates(payload)
    dispatcher = MessageDispatcher(WhatsAppBotClient(settings))

    results = [await dispatcher.handle_incoming(update, session) for update in updates]
    return {
        "ok": True,
        "handled": sum(not r.duplicate for r in results),
        "duplicates": sum(r.duplicate for r in results),
        "replies_sent": sum(r.reply_sent for r in results),
    }
