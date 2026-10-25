# Safeguarding policy

Many HerChoice AI users are adolescent girls. Their safety comes before every other goal, including growth.

## Principles

1. **Do no harm.** HerChoice provides information and navigation. It never diagnoses, prescribes or replaces a health worker.
2. **Age-appropriate by default.** Content has a minimum age band (10–14, 15–19, 20+). If a user does not give her age, she receives only content suitable for the youngest band.
3. **Never blame.** Responses to disclosures say clearly that what happened is not her fault.
4. **Her choice.** No referral, follow-up or data sharing happens without her explicit consent.
5. **Discreet.** Neutral channel names, no stored history by default, and a one-word delete command protect girls using shared phones.

## Safety layer

Every message is checked before any answer:

| Signal | Example | Response |
|---|---|---|
| Abuse, violence, coercion, forced marriage | "he forced me", "an yi min fyade" | Supportive message; offer of verified protection service; reminder of DELETE |
| Danger signs | heavy bleeding, fainting, severe pain, bleeding in pregnancy | Advice to seek care now; offer of nearest verified facility |
| No approved answer | anything outside the library | Honest "I don't have an approved answer"; offer of a health worker |

The word lists in `src/herchoice/safety.py` are deliberately broad (a false alarm is safer than a missed case). **Hausa terms are drafts** and must be validated by the Hausa language lead and the safeguarding lead before the pilot.

## Before any pilot

- [ ] Safeguarding lead approves all safety messages in English and Hausa.
- [ ] Every facility in the directory is verified in person or by phone, with `verified_by` and `verified_on` recorded.
- [ ] Protection services in each pilot LGA are mapped and confirmed willing to receive referrals.
- [ ] All team members complete safeguarding and data-protection training.
- [ ] User testing with minors uses informed consent and parental consent, approved by an ethics review.
- [ ] `HERCHOICE_ALLOW_DRAFT=false` in production.

## Incident response

Any safeguarding concern raised by a user, partner or team member is reported to the safeguarding lead within 24 hours, recorded without identifying the user, and reviewed by the founders. Serious incidents are reported to partners, including UNICEF, as agreed in funding terms.

Safeguarding lead: Khadija Adamu.
