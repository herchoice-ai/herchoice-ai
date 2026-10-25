"""The HerChoice conversation engine. Channel-independent: WhatsApp, voice line, USSD and the CLI all call it.

Order of every turn:
  1. commands (DELETE always works, first),
  2. pending steps (age group, referral consent, location),
  3. safety check,
  4. retrieval from the approved library,
  5. optional grounded rephrasing,
  6. reply, with an offer of referral when useful.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import llm, safety
from .config import Settings
from .content import AGE_BANDS, Library
from .messages import command_of, msg
from .privacy import SessionStore, anonymous_id
from .referral import Directory
from .retrieval import Retriever

AGE_CHOICES = {"1": AGE_BANDS[0], "2": AGE_BANDS[1], "3": AGE_BANDS[2]}


@dataclass(frozen=True)
class Reply:
    text: str
    language: str
    flag: str = safety.Flag.NONE.value
    entry_id: str | None = None


class Engine:
    def __init__(self, settings: Settings, library: Library | None = None, directory: Directory | None = None):
        self.settings = settings
        self.library = library or Library.load(settings.content_path)
        self.directory = directory or Directory.load(settings.facilities_path)
        self.retriever = Retriever(self.library)
        self.sessions = SessionStore(settings.session_ttl_seconds, settings.default_language)
        self._service_wanted: dict[str, str] = {}

    # ---- public -------------------------------------------------------------------------------
    def handle(self, raw_user_id: str, text: str) -> Reply:
        anon = anonymous_id(raw_user_id, self.settings.id_secret)
        text = (text or "").strip()
        command = command_of(text)

        # DELETE is checked before anything else and needs no confirmation.
        if command == "delete":
            lang = self.sessions.get(anon).language
            self.sessions.delete(anon)
            self._service_wanted.pop(anon, None)
            return Reply(msg("deleted", lang), lang)

        session = self.sessions.get(anon)
        lang = session.language
        self.sessions.remember(anon, text)

        if command == "hausa" or command == "english":
            session.language = "ha" if command == "hausa" else "en"
            return Reply(msg("language_set", session.language), session.language)
        if command == "menu":
            return Reply(msg("menu", lang), lang)
        if command == "save":
            session.save_history = True
            return Reply(msg("saved_on", lang), lang)
        if command == "age":
            session.awaiting = "age_band"
            return Reply(msg("ask_age", lang), lang)
        if command == "services":
            session.awaiting = "location"
            self._service_wanted[anon] = "srh"
            return Reply(msg("ask_location", lang), lang)

        # Pending steps
        if session.awaiting == "age_band":
            if text in AGE_CHOICES or text == "0":
                session.age_band = AGE_CHOICES.get(text)
                session.awaiting = None
                pending = session.pending_question
                session.pending_question = None
                if pending and self._is_real_question(pending, session.age_band):
                    return self._answer(anon, pending)
                return Reply(msg("age_saved", lang), lang)  # first message was a greeting
            return Reply(msg("ask_age", lang), lang)

        if session.awaiting == "referral_consent":
            session.awaiting = None
            if command == "yes":
                session.awaiting = "location"
                return Reply(msg("ask_location", lang), lang)
            # Anything else is treated as a new question.

        if session.awaiting == "location":
            session.awaiting = None
            return self._facilities(anon, text, lang)

        # First contact: welcome and ask age group once, keeping the question to answer next.
        if session.age_band is None and not session.age_asked:
            session.age_asked = True
            session.awaiting = "age_band"
            session.pending_question = text if text and command is None else None
            return Reply(f"{msg('welcome', lang)}\n\n{msg('ask_age', lang)}", lang)

        return self._answer(anon, text)

    # ---- internals ----------------------------------------------------------------------------
    def _is_real_question(self, text: str, age_band: str | None) -> bool:
        """A first message counts as a question if it raises a safety flag or matches content."""
        if safety.check(text).flag is not safety.Flag.NONE:
            return True
        hits = self.retriever.search(text, age_band, include_drafts=self.settings.allow_draft)
        return bool(hits) and hits[0].score >= self.settings.min_score

    def _answer(self, anon: str, question: str) -> Reply:
        session = self.sessions.get(anon)
        lang = session.language

        check = safety.check(question)
        if check.flag is not safety.Flag.NONE:
            session.awaiting = "referral_consent"
            self._service_wanted[anon] = "protection" if check.flag is safety.Flag.PROTECTION else "emergency"
            key = "protection" if check.flag is safety.Flag.PROTECTION else "urgent_care"
            return Reply(msg(key, lang), lang, flag=check.flag.value)

        hits = self.retriever.search(question, session.age_band, include_drafts=self.settings.allow_draft)
        if not hits or hits[0].score < self.settings.min_score:
            session.awaiting = "referral_consent"
            self._service_wanted[anon] = "srh"
            return Reply(msg("no_answer", lang), lang)

        entry = hits[0].entry
        approved, used_lang = entry.answer(lang)
        if self.settings.llm_enabled:
            approved = llm.rephrase(question, approved, used_lang, self.settings.llm_base_url,
                                    self.settings.llm_api_key, self.settings.llm_model)
        parts = []
        if entry.review_status != "approved":
            parts.append(msg("draft_notice", lang))
        if used_lang != lang:
            parts.append(msg("fallback_language", lang))
        parts.append(approved)
        parts.append(msg("disclaimer", lang))
        if entry.referral_suggested:
            session.awaiting = "referral_consent"
            self._service_wanted[anon] = "contraception" if "contraception" in entry.tags else "srh"
            parts.append(msg("offer_services", lang))
        return Reply("\n\n".join(p for p in parts if p), lang, entry_id=entry.id)

    def _facilities(self, anon: str, place: str, lang: str) -> Reply:
        service = self._service_wanted.pop(anon, None)
        found = self.directory.find(place, service) or self.directory.find(place)
        if not found:
            return Reply(msg("no_facility", lang), lang)
        lines = [msg("facilities_intro", lang)] + [f"• {f.describe()}" for f in found]
        if any(f.is_example for f in found):
            lines.append(msg("example_data", lang))
        return Reply("\n".join(lines), lang)
