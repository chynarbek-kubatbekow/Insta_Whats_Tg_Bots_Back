from __future__ import annotations

from app.bots.instagram import parse_instagram_updates
from app.bots.whatsapp import parse_whatsapp_updates
from app.models.message import Channel


def test_parse_whatsapp_updates() -> None:
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.123",
                                    "from": "777",
                                    "text": {"body": "Hello"},
                                },
                            ]
                        }
                    }
                ]
            }
        ]
    }

    updates = parse_whatsapp_updates(payload)

    assert len(updates) == 1
    assert updates[0].channel == Channel.WHATSAPP
    assert updates[0].external_chat_id == "777"
    assert updates[0].external_message_id == "wamid.123"


def test_parse_instagram_updates() -> None:
    payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "17841400000000000",
                "messaging": [
                    {
                        "sender": {"id": "123456789"},
                        "recipient": {"id": "17841400000000000"},
                        "message": {"mid": "message-id", "text": "Hello"},
                    }
                ],
            }
        ],
    }

    updates = parse_instagram_updates(payload)

    assert len(updates) == 1
    assert updates[0].channel == Channel.INSTAGRAM
    assert updates[0].external_chat_id == "123456789"
    assert updates[0].external_message_id == "message-id"


def test_parse_instagram_updates_ignores_echo_and_self_messages() -> None:
    payload = {
        "object": "instagram",
        "entry": [
            {
                "messaging": [
                    {
                        "sender": {"id": "17841400000000000"},
                        "message": {"text": "Bot reply", "is_echo": True},
                    },
                    {
                        "sender": {"id": "17841400000000000"},
                        "message": {"text": "Test message", "is_self": True},
                    },
                ]
            }
        ],
    }

    assert parse_instagram_updates(payload) == []
