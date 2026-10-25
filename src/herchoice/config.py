"""Runtime settings, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class Settings:
    # Content and directory files
    content_path: Path = field(
        default_factory=lambda: Path(_env("HERCHOICE_CONTENT", str(REPO_ROOT / "content" / "library.json")))
    )
    facilities_path: Path = field(
        default_factory=lambda: Path(_env("HERCHOICE_FACILITIES", str(REPO_ROOT / "data" / "facilities.example.csv")))
    )
    # Privacy: secret used to turn phone numbers into anonymous codes.
    id_secret: str = field(default_factory=lambda: _env("HERCHOICE_ID_SECRET", "change-me-in-production"))
    # How long a conversation is kept in memory when the user has not opted in to saving.
    session_ttl_seconds: int = field(default_factory=lambda: int(_env("HERCHOICE_SESSION_TTL", "1800")))
    # Default language for replies: "ha" (Hausa) or "en" (English).
    default_language: str = field(default_factory=lambda: _env("HERCHOICE_DEFAULT_LANG", "ha"))
    # Minimum retrieval score for an answer to be given; below it, the user is offered a referral.
    min_score: float = field(default_factory=lambda: float(_env("HERCHOICE_MIN_SCORE", "1.0")))
    # Demo mode only: also answer from draft content, clearly labelled. Must be "false" in any pilot.
    allow_draft: bool = field(default_factory=lambda: _env("HERCHOICE_ALLOW_DRAFT", "false").lower() == "true")
    # Optional language model (any OpenAI-compatible endpoint, e.g. a self-hosted open-weight model).
    llm_base_url: str = field(default_factory=lambda: _env("HERCHOICE_LLM_BASE_URL"))
    llm_api_key: str = field(default_factory=lambda: _env("HERCHOICE_LLM_API_KEY"))
    llm_model: str = field(default_factory=lambda: _env("HERCHOICE_LLM_MODEL"))
    # WhatsApp Cloud API
    wa_token: str = field(default_factory=lambda: _env("WHATSAPP_TOKEN"))
    wa_phone_number_id: str = field(default_factory=lambda: _env("WHATSAPP_PHONE_NUMBER_ID"))
    wa_verify_token: str = field(default_factory=lambda: _env("WHATSAPP_VERIFY_TOKEN"))

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_base_url and self.llm_model)


def get_settings() -> Settings:
    return Settings()
