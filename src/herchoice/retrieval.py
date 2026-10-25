"""Bilingual BM25 retrieval over the approved content library.

Pure Python, no external services: the answer engine can run offline on low-cost hardware.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from .content import Entry, Library

# Very common words carry no meaning for search. Hausa list to be extended by the Hausa language lead.
STOPWORDS = {
    "en": {
        "a", "an", "the", "is", "are", "am", "i", "me", "my", "you", "your", "it", "to", "of", "and",
        "or", "in", "on", "for", "do", "does", "can", "what", "how", "when", "why", "should", "will",
        "be", "with", "about", "this", "that", "if", "there", "have", "has", "get",
    },
    "ha": {"da", "na", "ta", "a", "ne", "ce", "ko", "shin", "ina", "zan", "za", "mi", "me", "wannan", "kuma"},
}
ALL_STOPWORDS = STOPWORDS["en"] | STOPWORDS["ha"]

_TOKEN_RE = re.compile(r"[a-z0-9ƙɗɓƴ']+")


def normalise(text: str) -> str:
    """Lower-case, and map Hausa hooked letters to plain ones so either spelling matches."""
    text = text.lower()
    text = text.replace("ƙ", "k").replace("ɗ", "d").replace("ɓ", "b").replace("ƴ", "y").replace("'", "")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(normalise(text)) if t not in ALL_STOPWORDS and len(t) > 1]


@dataclass(frozen=True)
class Hit:
    entry: Entry
    score: float


class Retriever:
    def __init__(self, library: Library, k1: float = 1.5, b: float = 0.75) -> None:
        self.library = library
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(e.searchable_text())) for e in library.entries]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_len = sum(self.lengths) / max(len(self.lengths), 1)
        df: Counter[str] = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, age_band: str | None, limit: int = 3, include_drafts: bool = False) -> list[Hit]:
        terms = tokenize(query)
        hits: list[Hit] = []
        for entry, doc, length in zip(self.library.entries, self.docs, self.lengths):
            if not entry.allowed_for(age_band):
                continue
            if entry.review_status != "approved" and not (include_drafts and entry.review_status == "draft"):
                continue
            score = 0.0
            for t in terms:
                tf = doc.get(t, 0)
                if tf:
                    denom = tf + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                    score += self.idf[t] * tf * (self.k1 + 1) / denom
            if score > 0:
                hits.append(Hit(entry, score))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]
