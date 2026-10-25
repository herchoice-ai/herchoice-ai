# Architecture

HerChoice AI is one channel-independent **engine** with thin **channel adapters**. Everything is open source; there is no proprietary backend.

## Components

| Component | File | What it does |
|---|---|---|
| Engine | `src/herchoice/engine.py` | Runs each turn: commands → pending steps → safety → retrieval → optional rephrasing → reply |
| Safety layer | `src/herchoice/safety.py` | Detects danger signs (urgent care) and abuse disclosures (protection). Runs before any answer |
| Privacy | `src/herchoice/privacy.py` | Keyed hash of phone numbers, expiring sessions, opt-in history, instant deletion |
| Retrieval | `src/herchoice/retrieval.py` | Bilingual BM25 search over approved content, filtered by age band and review status |
| Content library | `content/library.json` | Versioned entries: questions, answers (en/ha), keywords, age band, sources, review status |
| Grounded rephrasing | `src/herchoice/llm.py` | Optional. Any OpenAI-compatible endpoint (e.g. a self-hosted open-weight model). Rejects rewrites that add numbers |
| Speech | `src/herchoice/speech.py` | Open Whisper model for Hausa speech-to-text; Meta MMS-TTS Hausa voice |
| Referral directory | `src/herchoice/referral.py` | Verified facilities by state and LGA, filtered by service, youth-friendly first |
| WhatsApp | `src/herchoice/channels/whatsapp.py` | Webhook parsing, voice-note download, replies |
| Service | `src/herchoice/app.py` | FastAPI: `/health`, `/chat`, `/webhook` |

## Design decisions

1. **Answers only from approved content.** Retrieval picks the answer; the language model may only reword it. This keeps every answer traceable to a reviewed entry and its sources.
2. **Safety first, every turn.** Protection takes priority over urgent care, which takes priority over answering.
3. **Cautious by default.** Unknown age → youngest band. Low retrieval score → referral, not a guess. Draft content is never shown unless demo mode is on, and then it is labelled.
4. **Lightweight core.** Retrieval is pure Python, so the text service runs on a small, low-cost server. Speech models load only when used.
5. **Channel-independent.** The voice line and USSD reuse the same engine; only the adapter changes.

## Data flow and storage

| Data | Stored? | How |
|---|---|---|
| Phone number | No | Converted to a 32-character keyed hash on arrival |
| Name | No | Never asked |
| Messages | No, by default | Kept in memory for the session only; saved only if the user sends `SAVE` |
| Age band, language | Session only | Expires after inactivity (default 30 minutes) |
| Aggregate statistics | Yes, anonymised | Counts by topic, referral and safety flag, for reporting and DHIS2 export |

## Interoperability

Aggregate, anonymised indicators (questions by topic, referrals offered and accepted, safety flags) are designed to be exported in a format that can be imported into DHIS2, the system Nigeria uses for national health statistics. The export module is on the roadmap for months 7–9.
