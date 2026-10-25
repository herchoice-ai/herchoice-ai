# Content review process

HerChoice AI answers only from the content library (`content/library.json`). No entry reaches users until it passes every step below.

## Workflow

| Step | Who | Output |
|---|---|---|
| 1. Draft in English from cited sources (WHO, UNICEF, Federal Ministry of Health) | Health Content Lead | `review_status: "draft"`, `sources` filled |
| 2. Clinical review: accuracy, safety, age band | Clinical reviewer (doctor, midwife or nurse) | Corrections; `min_age_band` confirmed |
| 3. Hausa translation, written for spoken use and low literacy | Hausa Language Lead | `answers.ha` filled |
| 4. Hausa back-check: does the Hausa say the same as the English? | Second Hausa speaker | Sign-off |
| 5. User testing with Hausa-speaking women and girls (with consent) | Community & Safeguarding Lead | Clarity feedback |
| 6. Approval | Clinical reviewer | `review_status: "approved"`, `reviewed_by`, `reviewed_on`, `version` +1 |

Any change to an approved answer goes back to step 2 and increases `version`.

## Entry format

```json
{
  "id": "emergency-contraception",
  "topic": "Emergency contraception",
  "questions": {"en": ["..."], "ha": ["..."]},
  "answers":   {"en": "...", "ha": "..."},
  "keywords":  {"en": ["..."], "ha": ["..."]},
  "min_age_band": "15-19",
  "sources": ["WHO Fact Sheet: Emergency contraception"],
  "review_status": "draft | approved | retired",
  "reviewed_by": "",
  "reviewed_on": "",
  "version": 1,
  "referral_suggested": true,
  "tags": ["contraception"]
}
```

## Writing rules

- Plain words, short sentences, under 90 words per answer, suitable for reading aloud.
- Neutral and non-judgemental: present options; never pressure a choice.
- Always say when to see a health worker.
- No brand names of medicines unless the clinical reviewer requires them.
- Numbers (days, doses, ages) only as stated in the cited source.

## Open decisions for the clinical lead

- Which contraception content is shown to the 10–14 age band, given that some girls in this band are married. Currently, contraception entries start at 15–19, and younger users are offered a referral instead.

## Current status (v0.1.0)

10 English entries drafted with sources; 0 approved; Hausa translations in progress. Interface messages in Hausa (`src/herchoice/messages.py`) are drafted and await review.
