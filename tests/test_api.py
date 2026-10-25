import importlib

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("HERCHOICE_ALLOW_DRAFT", "true")
    monkeypatch.setenv("HERCHOICE_DEFAULT_LANG", "en")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verify-me")
    import herchoice.app as app_module

    importlib.reload(app_module)
    return TestClient(app_module.app)


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["approved_entries"] >= 0


def test_chat_flow(client):
    client.post("/chat", json={"user": "t", "text": "hi"})
    client.post("/chat", json={"user": "t", "text": "2"})
    r = client.post("/chat", json={"user": "t", "text": "the condom broke"}).json()
    assert r["entry_id"] == "emergency-contraception"


def test_webhook_verification(client):
    ok = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "verify-me",
                                         "hub.challenge": "123"})
    assert ok.status_code == 200 and ok.text == "123"
    bad = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "wrong",
                                          "hub.challenge": "123"})
    assert bad.status_code == 403


def test_webhook_parsing():
    from herchoice.channels.whatsapp import parse_webhook

    body = {"entry": [{"changes": [{"value": {"messages": [
        {"from": "234800", "type": "text", "text": {"body": "Sannu"}},
        {"from": "234801", "type": "audio", "audio": {"id": "media-1"}},
    ]}}]}]}
    msgs = parse_webhook(body)
    assert [m.kind for m in msgs] == ["text", "audio"]
    assert msgs[0].text == "Sannu" and msgs[1].media_id == "media-1"
