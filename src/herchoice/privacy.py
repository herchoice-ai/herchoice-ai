"""Privacy by design.

* Phone numbers are never stored: they are turned into an anonymous code with a keyed hash.
* No names, no profiles. A session holds only language, age band and opt-in choices.
* Sessions expire automatically unless the user opts in to saving.
* One command deletes everything held about a user, immediately.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field


def anonymous_id(raw_id: str, secret: str) -> str:
    """Keyed hash: the same phone always maps to the same code, but the code cannot be reversed."""
    return hmac.new(secret.encode(), raw_id.encode(), hashlib.sha256).hexdigest()[:32]


@dataclass
class Session:
    language: str
    age_band: str | None = None
    save_history: bool = False
    awaiting: str | None = None  # e.g. "age_band", "location", "referral_consent"
    pending_question: str | None = None  # question asked before the age group was known
    age_asked: bool = False
    history: list[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)


class SessionStore:
    """In-memory store. A production deployment can swap in an encrypted store with the same interface."""

    def __init__(self, ttl_seconds: int, default_language: str) -> None:
        self.ttl = ttl_seconds
        self.default_language = default_language
        self._sessions: dict[str, Session] = {}

    def get(self, anon_id: str) -> Session:
        self._expire()
        session = self._sessions.get(anon_id)
        if session is None:
            session = Session(language=self.default_language)
            self._sessions[anon_id] = session
        session.last_seen = time.time()
        return session

    def remember(self, anon_id: str, text: str) -> None:
        session = self._sessions.get(anon_id)
        if session and session.save_history:
            session.history.append(text)

    def delete(self, anon_id: str) -> bool:
        return self._sessions.pop(anon_id, None) is not None

    def count(self) -> int:
        self._expire()
        return len(self._sessions)

    def _expire(self) -> None:
        now = time.time()
        stale = [k for k, s in self._sessions.items() if not s.save_history and now - s.last_seen > self.ttl]
        for k in stale:
            del self._sessions[k]
