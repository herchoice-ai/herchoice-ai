"""The approved content library: the only source HerChoice AI answers from."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

AGE_BANDS = ("10-14", "15-19", "20+")


@dataclass(frozen=True)
class Entry:
    id: str
    topic: str
    questions: dict[str, list[str]]
    answers: dict[str, str]
    keywords: dict[str, list[str]]
    min_age_band: str
    sources: list[str]
    review_status: str
    reviewed_by: str = ""
    reviewed_on: str = ""
    version: int = 1
    referral_suggested: bool = False
    tags: list[str] = field(default_factory=list)

    def answer(self, lang: str) -> tuple[str, str]:
        """Return (text, language actually used). Falls back to English if a translation is missing."""
        text = self.answers.get(lang, "").strip()
        if text:
            return text, lang
        return self.answers.get("en", "").strip(), "en"

    def allowed_for(self, age_band: str | None) -> bool:
        """Unknown age is treated as the youngest band, so content is always age-appropriate."""
        band = age_band if age_band in AGE_BANDS else AGE_BANDS[0]
        return AGE_BANDS.index(band) >= AGE_BANDS.index(self.min_age_band)

    def searchable_text(self) -> str:
        parts: list[str] = [self.topic]
        for qs in self.questions.values():
            parts.extend(qs)
        for kws in self.keywords.values():
            parts.extend(kws)
        parts.extend(self.tags)
        return " ".join(parts)


@dataclass
class Library:
    entries: list[Entry]
    version: str

    @classmethod
    def load(cls, path: Path) -> "Library":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        entries = []
        for item in raw["entries"]:
            if item["min_age_band"] not in AGE_BANDS:
                raise ValueError(f"{item['id']}: unknown age band {item['min_age_band']!r}")
            entries.append(Entry(**item))
        ids = [e.id for e in entries]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate entry ids in content library")
        return cls(entries=entries, version=raw.get("version", "0"))

    def get(self, entry_id: str) -> Entry | None:
        return next((e for e in self.entries if e.id == entry_id), None)
