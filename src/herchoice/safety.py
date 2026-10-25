"""Safety layer: runs on every message before any answer is given.

It looks for two kinds of signal:
  * danger signs that need urgent in-person care, and
  * disclosures of abuse, violence or coercion, which need a protection referral.

Word lists are deliberately cautious (they prefer a false alarm to a missed case).
Hausa terms are drafts and must be validated by the Hausa language lead and the
safeguarding lead before any pilot. See docs/SAFEGUARDING.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .retrieval import normalise

_WORD_RE = re.compile(r"[a-z0-9]+")


class Flag(str, Enum):
    NONE = "none"
    URGENT_CARE = "urgent_care"
    PROTECTION = "protection"


URGENT_PHRASES = {
    "en": [
        "heavy bleeding", "bleeding a lot", "soaking pads", "won't stop bleeding", "wont stop bleeding",
        "fainted", "fainting", "passed out", "severe pain", "very bad pain", "unbearable pain",
        "high fever", "fits", "convulsion", "seizure", "pregnant and bleeding", "bleeding in pregnancy",
        "can't breathe", "cant breathe", "unsafe abortion", "took something to end",
    ],
    "ha": [  # DRAFT — validate with Hausa language lead
        "zubar jini mai yawa", "jini mai yawa", "jini baya tsayawa", "suma", "na suma",
        "ciwo mai tsanani", "zazzabi mai zafi", "farfadiya",
    ],
}

PROTECTION_PHRASES = {
    "en": [
        "rape", "raped", "forced me", "forced to have sex", "abuse", "abused", "beats me", "hits me",
        "hurt me", "touched me", "threatened", "not safe at home", "married me off", "forced marriage",
        "he will kill", "violence",
    ],
    "ha": [  # DRAFT — validate with Hausa language lead and safeguarding lead
        "fyade", "an yi min fyade", "yana duka na", "yana dukana", "an tilasta min", "auren dole",
        "ana cin zarafi", "cin zarafi",
    ],
}


@dataclass(frozen=True)
class SafetyResult:
    flag: Flag
    matched: str = ""


def _words(text: str) -> str:
    """Normalise and strip punctuation, padded with spaces so phrases match on whole words."""
    return " " + " ".join(_WORD_RE.findall(normalise(text))) + " "


def _find(text: str, table: dict[str, list[str]]) -> str:
    padded = _words(text)
    for phrases in table.values():
        for phrase in phrases:
            if _words(phrase) in padded:
                return phrase
    return ""


def check(text: str) -> SafetyResult:
    """Protection takes priority over urgent care: a person disclosing abuse needs both, safely."""
    hit = _find(text, PROTECTION_PHRASES)
    if hit:
        return SafetyResult(Flag.PROTECTION, hit)
    hit = _find(text, URGENT_PHRASES)
    if hit:
        return SafetyResult(Flag.URGENT_CARE, hit)
    return SafetyResult(Flag.NONE)
