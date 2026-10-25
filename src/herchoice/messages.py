"""Fixed interface messages in English and Hausa.

Hausa text in this file is a DRAFT. Every line must be reviewed and signed off by the
Hausa language lead before any user sees it (tracked in docs/CONTENT_REVIEW.md).
"""

from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    "welcome": {
        "en": "Welcome to HerChoice. Ask any question about periods, family planning or your body. "
              "Your questions are private. Send MENU for options, or DELETE at any time to erase everything.",
        "ha": "Barka da zuwa HerChoice. Ki yi kowace tambaya game da al'ada, tsarin iyali ko jikinki. "
              "Tambayoyinki sirri ne. Aika MENU don zaɓuɓɓuka, ko GOGE a kowane lokaci don share komai.",
    },
    "ask_age": {
        "en": "So I can give answers right for your age, how old are you? "
              "Reply 1 for 10–14, 2 for 15–19, 3 for 20 or older, or 0 to skip.",
        "ha": "Don in ba ki amsar da ta dace da shekarunki, shekarunki nawa? "
              "Amsa 1 idan 10–14, 2 idan 15–19, 3 idan 20 ko fiye, ko 0 don tsallakewa.",
    },
    "age_saved": {
        "en": "Thank you. Now ask your question.",
        "ha": "Na gode. Yanzu ki yi tambayarki.",
    },
    "menu": {
        "en": "Options:\n• Ask any question in your own words\n• AGE – change your age group\n"
              "• HAUSA / ENGLISH – change language\n• SERVICES – find a verified health worker\n"
              "• SAVE – keep this chat (off by default)\n• DELETE – erase everything now",
        "ha": "Zaɓuɓɓuka:\n• Ki yi tambaya da kalmominki\n• SHEKARU – canza rukunin shekaru\n"
              "• HAUSA / ENGLISH – canza harshe\n• ASIBITI – nemo ma'aikacin lafiya da aka tantance\n"
              "• AJIYE – ajiye wannan hira (a kashe yake)\n• GOGE – share komai yanzu",
    },
    "deleted": {
        "en": "All your information has been deleted. You can start again at any time.",
        "ha": "An share duk bayananki. Kina iya sake farawa a kowane lokaci.",
    },
    "saved_on": {
        "en": "This chat will now be saved so you can continue later. Send DELETE to erase it.",
        "ha": "Za a ajiye wannan hira yanzu domin ki ci gaba daga baya. Aika GOGE don share ta.",
    },
    "language_set": {
        "en": "I will reply in English.",
        "ha": "Zan amsa da Hausa.",
    },
    "no_answer": {
        "en": "I do not have an approved answer to that yet. A verified health worker can help. "
              "Reply YES to see services near you, or ask in another way.",
        "ha": "Ba ni da amsar da aka amince da ita kan wannan tukuna. Ma'aikacin lafiya da aka tantance zai iya taimakawa. "
              "Amsa EH don ganin wuraren kusa da ke, ko ki sake tambaya ta wata hanya.",
    },
    "urgent_care": {
        "en": "What you describe may need urgent care. Please go to the nearest health facility now, "
              "or ask someone you trust to take you. Reply YES to see verified facilities near you.",
        "ha": "Abin da kika faɗa na iya buƙatar kulawa cikin gaggawa. Don Allah ki je asibiti mafi kusa yanzu, "
              "ko ki roƙi wanda kika amince da shi ya kai ki. Amsa EH don ganin asibitocin da aka tantance kusa da ke.",
    },
    "protection": {
        "en": "Thank you for telling me. What happened is not your fault, and you deserve to be safe. "
              "If you are in danger now, go to a safe place or a trusted adult. "
              "Reply YES to see verified support services near you. Send DELETE at any time to erase this chat.",
        "ha": "Na gode da kika faɗa min. Abin da ya faru ba laifinki ba ne, kuma kin cancanci ki kasance lafiya. "
              "Idan kina cikin haɗari yanzu, ki je wuri mai aminci ko wurin babba da kika amince da shi. "
              "Amsa EH don ganin wuraren taimako da aka tantance kusa da ke. Aika GOGE a kowane lokaci don share wannan hira.",
    },
    "ask_location": {
        "en": "Which local government area or state are you in?",
        "ha": "A wace ƙaramar hukuma ko jiha kike?",
    },
    "no_facility": {
        "en": "I could not find a verified service there yet. Please visit your nearest primary health centre.",
        "ha": "Ban sami wurin da aka tantance a can ba tukuna. Don Allah ki je cibiyar lafiya mafi kusa.",
    },
    "facilities_intro": {
        "en": "Verified services near you:",
        "ha": "Wuraren da aka tantance kusa da ke:",
    },
    "offer_services": {
        "en": "Reply YES if you would like to see verified services near you.",
        "ha": "Amsa EH idan kina so ki ga wuraren da aka tantance kusa da ke.",
    },
    "fallback_language": {
        "en": "",
        "ha": "(Wannan amsa ba ta da Hausa tukuna, saboda haka an ba da ita da Turanci.)",
    },
    "draft_notice": {
        "en": "[DEMO – draft content pending clinical review]",
        "ha": "[GWAJI – bayanin da ake jiran likitoci su duba]",
    },
    "disclaimer": {
        "en": "This is general health information, not a diagnosis.",
        "ha": "Wannan bayani ne na lafiya gaba ɗaya, ba gano cuta ba ne.",
    },
    "example_data": {
        "en": "[Demo data: these are example entries, not real facilities.]",
        "ha": "[Bayanan gwaji: waɗannan misalai ne, ba wurare na gaske ba.]",
    },
}

COMMANDS = {
    "delete": {"DELETE", "GOGE", "SHARE"},
    "menu": {"MENU", "HELP", "TAIMAKO"},
    "age": {"AGE", "SHEKARU"},
    "save": {"SAVE", "AJIYE"},
    "services": {"SERVICES", "ASIBITI", "CLINIC"},
    "hausa": {"HAUSA"},
    "english": {"ENGLISH", "TURANCI"},
    "yes": {"YES", "Y", "EH", "I", "TO"},
}


def msg(key: str, lang: str) -> str:
    entry = MESSAGES[key]
    return entry.get(lang) or entry["en"]


def command_of(text: str) -> str | None:
    word = text.strip().upper().rstrip(".!")
    for name, words in COMMANDS.items():
        if word in words:
            return name
    return None
