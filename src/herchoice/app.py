"""HTTP service: WhatsApp webhook, a simple chat API for testing, and a health check.

Run:  uvicorn herchoice.app:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from . import __version__, speech
from .channels import whatsapp
from .config import get_settings
from .engine import Engine

settings = get_settings()
engine = Engine(settings)
app = FastAPI(title="HerChoice AI", version=__version__)


class ChatIn(BaseModel):
    user: str
    text: str


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": __version__,
        "content_version": engine.library.version,
        "approved_entries": sum(e.review_status == "approved" for e in engine.library.entries),
        "active_sessions": engine.sessions.count(),
    }


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    """Test endpoint used by the demo and by partners evaluating the engine."""
    reply = engine.handle(body.user, body.text)
    return {"reply": reply.text, "language": reply.language, "flag": reply.flag, "entry_id": reply.entry_id}


@app.get("/webhook", response_class=PlainTextResponse)
def verify(mode: str = Query("", alias="hub.mode"), token: str = Query("", alias="hub.verify_token"),
           challenge: str = Query("", alias="hub.challenge")) -> str:
    if mode == "subscribe" and settings.wa_verify_token and token == settings.wa_verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")


def _process(incoming: whatsapp.Incoming) -> None:
    text = incoming.text
    if incoming.kind == "audio":
        try:
            audio = whatsapp.download_media(incoming.media_id, settings.wa_token)
            lang = engine.sessions.get(engine_anon(incoming.sender)).language
            text = speech.transcribe(audio, lang)
        except Exception:
            text = ""
    reply = engine.handle(incoming.sender, text) if text else engine.handle(incoming.sender, "MENU")
    whatsapp.send_text(incoming.sender, reply.text, settings.wa_token, settings.wa_phone_number_id)


def engine_anon(sender: str) -> str:
    from .privacy import anonymous_id

    return anonymous_id(sender, settings.id_secret)


@app.post("/webhook")
async def receive(request: Request, tasks: BackgroundTasks) -> dict:
    body = await request.json()
    for incoming in whatsapp.parse_webhook(body):
        tasks.add_task(_process, incoming)
    return {"received": True}
