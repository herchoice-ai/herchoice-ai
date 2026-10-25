# HerChoice AI

**Private, Hausa-first reproductive health information and referral for women and girls.**

HerChoice AI lets women and adolescent girls in Northern Nigeria ask questions about menstrual health, contraception and fertility, by voice or text, in Hausa, on WhatsApp, a voice line or a basic phone. It answers only from a clinician-reviewed content library, protects privacy by design, and, with the user's consent, connects her to a verified health worker.

Built by **MUMSA Consanguinity Limited** (Nigeria). Code under **Apache 2.0**; content under **CC BY 4.0**.

> **Status: working prototype (v0.1.0).** The conversation engine, safety layer, privacy controls, referral flow and WhatsApp integration run and are tested. Health content is **draft** until our clinical lead approves it, and Hausa translations are in progress. See [Project status](#project-status).

---

## The problem

- **20%** of Nigerian women have an unmet need for family planning (Federal Ministry of Health and Social Welfare, Dec 2024).
- Only **3.3%** of married girls aged 15–19 use a modern contraceptive method (Population Council analysis of NDHS 2023–24).
- Hausa has about **58 million** first-language speakers, but reliable health information is rarely available in spoken Hausa.
- Stigma, distance, cost, low literacy and **shared family phones** stop women and girls from asking.

## What HerChoice AI does

| | |
|---|---|
| **Hausa voice** | She speaks her question and hears the answer, so reading is not required. |
| **Works on weak networks** | WhatsApp voice notes and text today; voice line and USSD for basic phones next. |
| **Trusted answers** | Answers come only from content reviewed by clinicians against WHO and Federal Ministry of Health guidance. |
| **Age-appropriate** | Content is matched to age bands 10–14, 15–19 and 20+. An unknown age gets the most cautious content. |
| **Safety layer** | Danger signs trigger urgent-care advice; disclosures of abuse trigger a protection referral. |
| **Consent and privacy** | No names, no stored phone numbers, no history by default, and one-command deletion (`DELETE` / `GOGE`). |
| **Verified referrals** | With her consent, she sees verified, youth-friendly services near her. |

## How it works

```
 WhatsApp / voice line / USSD
            │  voice note or text (Hausa or English)
            ▼
 ┌──────────────────────┐     ┌──────────────────────────────┐
 │ Speech-to-text       │     │ Privacy                      │
 │ open Whisper model   │     │ phone → anonymous code       │
 │ (Hausa)              │     │ no names · expiring sessions │
 └──────────┬───────────┘     └──────────────────────────────┘
            ▼
 ┌──────────────────────┐  danger sign / abuse  ┌─────────────────────┐
 │ Safety layer         │──────────────────────▶│ Urgent care or      │
 │ (runs first, always) │                       │ protection referral │
 └──────────┬───────────┘                       └─────────────────────┘
            ▼
 ┌──────────────────────┐     ┌──────────────────────────────┐
 │ Retrieval (BM25)     │◀────│ Approved content library     │
 │ bilingual, age-aware │     │ clinician-reviewed, CC BY 4.0│
 └──────────┬───────────┘     └──────────────────────────────┘
            ▼
 ┌──────────────────────┐
 │ Optional grounded LLM│  rewrites the approved answer to fit the question;
 │ rephrasing           │  any new number or fact → approved text used instead
 └──────────┬───────────┘
            ▼
   Reply (text + Hausa voice) → offer of verified referral, with consent
```

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Try it in 2 minutes

Requires Python 3.10+.

```bash
git clone https://github.com/<your-org>/herchoice-ai.git
cd herchoice-ai
pip install -e ".[dev]"

python -m herchoice.cli --lang en     # English demo
python -m herchoice.cli               # Hausa demo (default)
```

Try: `Is my period normal?`, `the condom broke`, `YES`, `Nassarawa`, `MENU`, `DELETE`.

The demo shows draft content with a visible **[DEMO – draft content pending clinical review]** label. Run with `--approved-only` to see exactly what a pilot user would see.

### Run the service

```bash
cp .env.example .env          # then fill in your values
uvicorn herchoice.app:app --host 0.0.0.0 --port 8000
```

| Endpoint | Purpose |
|---|---|
| `GET /health` | Status, content version, number of approved entries |
| `POST /chat` | `{"user": "...", "text": "..."}` → reply (for testing and partners) |
| `GET /webhook` | WhatsApp Cloud API verification |
| `POST /webhook` | WhatsApp messages in (text and voice notes) |

Voice support: `pip install -e ".[speech]"` (open Whisper for Hausa speech-to-text, Meta MMS-TTS Hausa voice).

### Run the tests

```bash
pytest
```

The tests check retrieval, age bands, the safety layer, Hausa commands, deletion, anonymous IDs, the grounding check on the language model, and the HTTP API.

## Repository layout

```
src/herchoice/
  engine.py        conversation engine (channel-independent)
  safety.py        danger-sign and abuse-disclosure detection
  privacy.py       anonymous IDs, expiring sessions, deletion
  retrieval.py     bilingual BM25 search over approved content
  content.py       content library model and age bands
  referral.py      verified facility directory
  llm.py           optional grounded rephrasing (OpenAI-compatible, open-weight models)
  speech.py        Hausa speech-to-text and text-to-speech (open models)
  messages.py      interface messages in English and Hausa
  channels/whatsapp.py   WhatsApp Cloud API adapter
  app.py           FastAPI service
  cli.py           terminal demo
content/library.json     health content (CC BY 4.0), with sources and review status
data/facilities.example.csv   example directory format (not real facilities)
docs/                    architecture, safeguarding, privacy, content review, roadmap
tests/                   automated tests
```

## Safety and safeguarding

HerChoice AI provides health **information and navigation**. It does not diagnose, prescribe or replace a health worker. Every message passes the safety layer before any answer is given. See [docs/SAFEGUARDING.md](docs/SAFEGUARDING.md) and [docs/PRIVACY.md](docs/PRIVACY.md). We follow the Nigeria Data Protection Act 2023.

## Project status

| Area | Status |
|---|---|
| Conversation engine, safety layer, privacy, referral flow | Built and tested |
| WhatsApp text integration | Built and tested |
| Hausa speech in/out (open models) | Integrated; accuracy testing with Hausa speakers planned |
| Content library | 10 draft entries in English with sources; clinical review and Hausa translation in progress |
| Interface messages in Hausa | Drafted; review by Hausa language lead in progress |
| Verified facility directory | Format ready; facilities to be verified for the pilot LGAs |
| Voice line and USSD channels | Planned (same engine) |

## Roadmap (12 months)

| Months | Milestones |
|---|---|
| 1–3 | 500 clinician-approved Hausa answers; Hausa speech accuracy tested with 100 users; public release |
| 4–6 | Pilot in 2 local government areas in Kano State; 2,000 users; 30 verified health workers |
| 7–9 | Independent privacy and safeguarding audit; pregnancy danger-sign module; State Primary Health Care Board agreement |
| 10–12 | 10,000 users in 3 LGAs; first institutional licence; public impact report |

Full plan: [docs/ROADMAP.md](docs/ROADMAP.md).

## Team

| Name | Role |
|---|---|
| Khadija Ashiru | Founder & CEO |
| Sulaiman Ashiru | Co-founder, CTO & AI Lead |
| Fatima Abdullahi Yahaya | Co-founder, Health Content Lead |
| Khadija Adamu | Co-founder, Community & Safeguarding Lead |
| Fatima Muftau | Co-founder, Hausa Language Lead |
| Precious Maro Ekeh | Co-founder, Operations & Partnerships Lead |

## Contributing

We welcome contributions, especially Hausa language review, clinical review and accessibility testing. See [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md). Report security or safeguarding concerns privately: [SECURITY.md](SECURITY.md).

## Licence

- **Code:** [Apache License 2.0](LICENSE)
- **Health content** (`content/`) and **documentation** (`docs/`): [Creative Commons Attribution 4.0](LICENSE-CONTENT.md)

Copyright © 2026 MUMSA Consanguinity Limited.
