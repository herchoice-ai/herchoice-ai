"""Optional language-model step: rephrase an approved answer so it fits the user's exact question.

Retrieval-augmented and tightly constrained: the model sees only the approved answer and may not
add facts. If it adds any number not in the approved text, or the call fails, the approved text
is used unchanged. Works with any OpenAI-compatible endpoint, including self-hosted open-weight models.
"""

from __future__ import annotations

import re

SYSTEM_PROMPT = (
    "You help women and girls understand reproductive health. Rewrite the APPROVED ANSWER so it directly "
    "answers the QUESTION in simple, kind, respectful {language}. Use ONLY facts in the APPROVED ANSWER. "
    "Do not add medical facts, numbers, medicines or advice. Do not diagnose. Keep it under 90 words."
)

_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def _numbers(text: str) -> set[str]:
    return set(_NUM.findall(text))


def is_grounded(candidate: str, approved: str) -> bool:
    """Reject any rewrite that introduces numbers the clinicians did not approve."""
    return bool(candidate.strip()) and _numbers(candidate) <= _numbers(approved)


def rephrase(question: str, approved: str, language: str, base_url: str, api_key: str, model: str,
             timeout: float = 8.0) -> str:
    try:
        import httpx  # optional dependency
    except ImportError:
        return approved
    lang_name = "Hausa" if language == "ha" else "English"
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.format(language=lang_name)},
            {"role": "user", "content": f"QUESTION: {question}\n\nAPPROVED ANSWER: {approved}"},
        ],
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        r = httpx.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        candidate = r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return approved
    return candidate if is_grounded(candidate, approved) else approved
