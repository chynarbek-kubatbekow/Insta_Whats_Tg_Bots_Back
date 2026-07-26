# Aruu Beauty Meta Bot

FastAPI backend for the Aruu Beauty demo salon on Instagram Direct and
WhatsApp Cloud API. Telegram is not
registered, configured, or called by the application.

## What it does

- accepts Meta webhook verification requests;
- verifies every POST webhook with `X-Hub-Signature-256`;
- parses Instagram text/postback events and WhatsApp text/button/list replies;
- ignores delivery/status events, echoes, deleted, and unsupported messages;
- deduplicates retried webhook messages by the external message ID;
- stores channel-separated conversation history in PostgreSQL;
- answers only from active `knowledge_entries` through Groq;
- splits outgoing messages to channel-safe lengths.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Configure the variables documented in `.env.example`. The public webhook URLs
must use HTTPS:

- `GET/POST https://YOUR_HOST/webhooks/whatsapp`
- `GET/POST https://YOUR_HOST/webhooks/instagram`

Use the matching `*_VERIFY_TOKEN` in the Meta webhook subscription. Subscribe
WhatsApp to the `messages` field and Instagram to messaging events supported by
your Meta app.

## Render deployment

`render.yaml` starts the service with:

```text
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Alembic creates the schema and seeds Aruu Beauty exactly once. In Render,
create a Blueprint from this repository or create a Python web service manually,
then copy every value from `.env.render.example` into **Environment**. Keep the
real `.env` out of Git.

After Render reports `Live`, use these two independent callback URLs:

- WhatsApp: `https://YOUR-SERVICE-NAME.onrender.com/webhooks/whatsapp`
- Instagram: `https://YOUR-SERVICE-NAME.onrender.com/webhooks/instagram`

The verification URL and event callback URL are the same for each platform.
WhatsApp must use `WHATSAPP_VERIFY_TOKEN`; Instagram must use
`INSTAGRAM_VERIFY_TOKEN`. These tokens are values you invent and enter both in
Render and the corresponding Meta dashboard. App secrets and access tokens come
from Meta and must never be placed in callback URLs.

Request flow:

```text
WhatsApp or Instagram
  -> platform-specific webhook
  -> signature verification and event parsing
  -> shared MessageDispatcher and grounded Groq answer
  -> platform-specific Graph API client
  -> reply to the same user on the originating platform
```

## API

- `GET /health`
- `GET/POST /webhooks/whatsapp`
- `GET/POST /webhooks/instagram`
- `/api/v1/staged-records` remains protected by `X-API-Key`

## Verification

```powershell
ruff check .
pytest
alembic upgrade head
```
