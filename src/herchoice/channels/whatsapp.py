"""WhatsApp Cloud API adapter: receive text and voice notes, send replies.

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
Phone numbers arrive from WhatsApp and are passed straight to the engine, which turns them into an
anonymous code before anything is stored. They are never logged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

GRAPH = os.environ.get("WHATSAPP_GRAPH_URL", "https://graph.facebook.com/v20.0")


@dataclass(frozen=True)
class Incoming:
    sender: str
    kind: str  # "text" or "audio"
    text: str = ""
    media_id: str = ""


def parse_webhook(body: dict[str, Any]) -> list[Incoming]:
    """Extract user messages from a webhook payload; ignore delivery receipts and other events."""
    out: list[Incoming] = []
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            for m in change.get("value", {}).get("messages", []):
                sender = m.get("from", "")
                if m.get("type") == "text":
                    out.append(Incoming(sender, "text", text=m["text"]["body"]))
                elif m.get("type") == "audio":
                    out.append(Incoming(sender, "audio", media_id=m["audio"]["id"]))
                elif m.get("type") == "interactive":
                    reply = m["interactive"].get("button_reply") or m["interactive"].get("list_reply") or {}
                    out.append(Incoming(sender, "text", text=reply.get("title", "")))
    return out


def download_media(media_id: str, token: str) -> bytes:
    import httpx

    headers = {"Authorization": f"Bearer {token}"}
    meta = httpx.get(f"{GRAPH}/{media_id}", headers=headers, timeout=15)
    meta.raise_for_status()
    audio = httpx.get(meta.json()["url"], headers=headers, timeout=30)
    audio.raise_for_status()
    return audio.content


def send_text(to: str, text: str, token: str, phone_number_id: str) -> None:
    import httpx

    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text[:4096]}}
    r = httpx.post(f"{GRAPH}/{phone_number_id}/messages", json=payload,
                   headers={"Authorization": f"Bearer {token}"}, timeout=15)
    r.raise_for_status()
