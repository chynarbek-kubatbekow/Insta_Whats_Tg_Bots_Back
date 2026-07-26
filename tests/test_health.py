from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import instagram, whatsapp
from app.core.config import Settings
from app.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_accepts_head() -> None:
    client = TestClient(app)
    response = client.head("/health")

    assert response.status_code == 200
    assert response.content == b""


def test_openapi_contains_expected_routes() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/staged-records" in paths
    assert "/api/v1/staged-records/{record_id}/activate" in paths
    assert "/webhooks/telegram" not in paths
    assert "/webhooks/whatsapp" in paths
    assert "/webhooks/instagram" in paths


def test_staged_records_requires_api_key() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/staged-records", json={"data": {"name": "Test"}})

    assert response.status_code == 401


def test_whatsapp_webhook_verification(monkeypatch) -> None:
    settings = Settings(whatsapp_verify_token="wa-test-token")
    monkeypatch.setattr(whatsapp, "get_settings", lambda: settings)
    client = TestClient(app)

    response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wa-test-token",
            "hub.challenge": "12345",
        },
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_instagram_webhook_verification(monkeypatch) -> None:
    settings = Settings(instagram_verify_token="ig-test-token")
    monkeypatch.setattr(instagram, "get_settings", lambda: settings)
    client = TestClient(app)

    response = client.get(
        "/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "ig-test-token",
            "hub.challenge": "67890",
        },
    )

    assert response.status_code == 200
    assert response.text == "67890"


def test_meta_webhooks_reject_invalid_signature(monkeypatch) -> None:
    whatsapp_settings = Settings(whatsapp_app_secret="wa-secret")
    instagram_settings = Settings(instagram_app_secret="ig-secret")
    monkeypatch.setattr(whatsapp, "get_settings", lambda: whatsapp_settings)
    monkeypatch.setattr(instagram, "get_settings", lambda: instagram_settings)
    client = TestClient(app)

    wa_response = client.post(
        "/webhooks/whatsapp",
        content=b'{"entry":[]}',
        headers={"x-hub-signature-256": "sha256=invalid"},
    )
    ig_response = client.post(
        "/webhooks/instagram",
        content=b'{"entry":[]}',
        headers={"x-hub-signature-256": "sha256=invalid"},
    )

    assert wa_response.status_code == 403
    assert ig_response.status_code == 403
