# Privacy by design

HerChoice AI is built to comply with the **Nigeria Data Protection Act 2023** and to protect users on shared phones.

## What we collect, and what we don't

| We do not collect | We collect (only when needed) |
|---|---|
| Names | Language choice and age band, for the current session |
| Phone numbers (they are converted to an anonymous code) | Messages, only if the user sends `SAVE` |
| Location history | The LGA a user types, only to show nearby services, then discarded |
| Photos, contacts, device data | Anonymous counts for reporting (topic, referral, safety flag) |

## User controls

| Command | English | Hausa |
|---|---|---|
| Delete everything now | `DELETE` | `GOGE` |
| Save this chat | `SAVE` | `AJIYE` |
| Change language | `ENGLISH` | `HAUSA` |
| See options | `MENU` | `TAIMAKO` |

## Technical measures

- **Anonymous IDs:** phone numbers are turned into a keyed hash (HMAC-SHA-256) using a secret held only on the server. The code cannot be reversed into the number.
- **Short-lived sessions:** without `SAVE`, sessions expire after 30 minutes of inactivity (configurable).
- **No logging of message content** in production.
- **Encryption in transit:** all traffic between WhatsApp and our service uses HTTPS.
- **Least privilege:** only the CTO and named engineers can access production servers.
- **Independent privacy audit** in months 7–9 of the pilot.

## Sharing

We never sell or share identifiable data. Partners receive only anonymised, aggregate statistics. A referral shares nothing about the user unless she chooses to contact the service herself.
