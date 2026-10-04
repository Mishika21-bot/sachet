"""Regex/keyword red flags in English, Hindi (Devanagari), and Hinglish. No LLM required."""

from __future__ import annotations

import re

from app.models import RedFlag

# Each rule: id, bilingual labels, compiled patterns that must work in all three languages.
_RULES: list[tuple[str, str, str, list[re.Pattern[str]]]] = [
    (
        "guaranteed_returns",
        "Guaranteed / fixed / doubling returns",
        "गारंटीड / निश्चित / डबल रिटर्न का वादा",
        [
            re.compile(
                r"(?:guaranteed|assured|fixed|sure[\s\-]?shot)\s+"
                r"(?:\d+\s*%\s+)?(?:returns?|profits?|income|munafa)|"
                r"(?:\d+\s*%\s+)?(?:guaranteed|assured|fixed|sure[\s\-]?shot)\s+"
                r"(?:returns?|profits?|income)|"
                r"double\s+(your\s+)?(money|paisa)|"
                r"risk[\s\-]?free\s+(returns?|profit)",
                re.I,
            ),
            re.compile(
                r"(गारंटी(ड)?|आश्वस्त|निश्चित|पक्का|श्योर[\s\-]?शॉट)\s*"
                r"(\d+\s*%\s*)?(रिटर्न|मुनाफा|नफा)|"
                r"(\d+\s*%\s*)?(गारंटी(ड)?|आश्वस्त|निश्चित|पक्का)\s*(रिटर्न|मुनाफा|नफा)|"
                r"डबल\s*(पैसा|रिटर्न)|दोगुना\s*(पैसा|मुनाफा)",
            ),
            re.compile(
                r"(pakka|assured|fixed|sure[\s\-]?shot|guarantee(?:d)?(?:\s+wala)?)\s+"
                r"(?:\d+\s*%\s+)?(profit|munafa|returns?)|"
                r"(?:\d+\s*%\s+)?(pakka|assured|fixed|sure[\s\-]?shot|guaranteed)\s+"
                r"(profit|munafa|returns?)|"
                r"double\s+paisa|risk\s*free\s+profit",
                re.I,
            ),
        ],
    ),
    (
        "urgency_pressure",
        "Urgency or pressure to act immediately",
        "तुरंत कार्रवाई का दबाव / जल्दबाज़ी",
        [
            re.compile(
                r"act\s+now|last\s+chance|limited\s+(seats|slots|time)|today\s+only|"
                r"offer\s+expires|hurry|don'?t\s+miss|before\s+it'?s\s+too\s+late",
                re.I,
            ),
            re.compile(
                r"आज\s*ही|अभी\s*(करो|करें|इन्वेस्ट)|सीमित\s*(सीट|समय|ऑफर)|आखिरी\s*(मौका|चांस)|"
                r"जल्दी\s*(करो|करें)|मौका\s*मत\s*गवा[ओौ]",
            ),
            re.compile(
                r"jaldi\s+(karo|kar\s+do)|abhi\s+(invest|karo)|last\s+chance|limited\s+seats|"
                r"aaj\s+hi|mat\s+gawao",
                re.I,
            ),
        ],
    ),
    (
        "personal_payment",
        "Payment asked to a personal UPI / bank account",
        "व्यक्तिगत यूपीआई / बैंक खाते में भुगतान की माँग",
        [
            re.compile(
                r"pay.{0,50}(\[UPI\]|\bupi\b|gpay|phonepe|personal\s+account)|"
                r"pay\s+(to\s+)?(my\s+)?(personal\s+)?(upi|account|gpay|phonepe)|"
                r"send\s+(money|funds|rs|inr).{0,40}(personal|\[UPI\]|upi)|"
                r"personal\s+(upi|account|bank)|transfer.{0,30}(my\s+)?upi|"
                r"\[UPI\]",
                re.I,
            ),
            re.compile(
                r"(मेरे|अपने)\s*(यूपीआई|UPI|खाते|अकाउंट)|व्यक्तिगत\s*(यूपीआई|खाता|अकाउंट)|"
                r"(भेजो|भेजें|पेमेंट).{0,30}(यूपीआई|UPI|खाते)",
            ),
            re.compile(
                r"mere\s+(upi|account)|personal\s+(upi|account)|apna\s+upi|"
                r"paise\s+(bhejo|bhej\s+do).{0,20}(upi|account)|mera\s+(account|upi)",
                re.I,
            ),
        ],
    ),
    (
        "apk_private_app",
        "Asks to download an APK or private / unofficial app",
        "एपीके या निजी / अनौपचारिक ऐप डाउनलोड करने को कहा गया",
        [
            re.compile(
                r"\bapk\b|sideload|install\s+(this\s+)?app|private\s+app|"
                r"not\s+(on\s+)?(play\s*store|app\s*store)|download.{0,20}(link|app|apk)",
                re.I,
            ),
            re.compile(
                r"एपीके|apk\s*डाउनलोड|प्ले\s*स्टोर\s*(से\s*)?(नहीं|मत)|निजी\s*ऐप|"
                r"ऐप\s*इंस्टॉल|लिंक\s*से\s*डाउनलोड",
            ),
            re.compile(
                r"apk\s+download|play\s*store\s+se\s+nahi|private\s+app|"
                r"app\s+install\s+karo|sideload",
                re.I,
            ),
        ],
    ),
    (
        "remote_access",
        "Remote-access app (AnyDesk / TeamViewer-style)",
        "रिमोट-एक्सेस ऐप (AnyDesk / TeamViewer जैसा)",
        [
            re.compile(
                r"anydesk|teamviewer|ultraviewer|rustdesk|quicksupport|"
                r"remote\s+(access|desktop|control)|screen\s*share\s+(app|tool)|give\s+(me\s+)?otp",
                re.I,
            ),
            re.compile(
                r"एनीडेस्क|टीमव्यूअर|रिमोट\s*(एक्सेस|कंट्रोल)|स्क्रीन\s*शेयर|"
                r"ओटीपी\s*(बताओ|दो|शेयर)",
            ),
            re.compile(
                r"anydesk|teamviewer|remote\s+access|screen\s+share\s+karo|"
                r"otp\s+(batao|do|share)",
                re.I,
            ),
        ],
    ),
    (
        "lookalike_broker",
        "Lookalike / unofficial broker or exchange link",
        "ब्रोकर / एक्सचेंज जैसा नकली या अनौपचारिक लिंक",
        [
            re.compile(
                r"zerodhaa|zer0dha|zerodha-(login|app)|growww|groww-(login|app)|"
                r"upstoxx|angelonee|nse-?india\.(?!com\b)|bse-?india\.(?!com\b)|"
                r"sebi-(verify|login|register|india)|sebiindia\.|"
                r"(zerodha|groww|upstox|angelone|nseindia|bseindia|sebi)"
                r"[a-z0-9\-]*\.(tk|ml|ga|cf|gq|xyz|top|click|link|club)",
                re.I,
            ),
            re.compile(
                r"नकली\s*(ब्रोकर|वेबसाइट|लिंक)|फर्जी\s*(ब्रोकर|साइट)|"
                r"सेबी\s*वेरिफाई\s*लिंक|ब्रोकर\s*जैसी\s*साइट",
            ),
            re.compile(
                r"nakli\s+(broker|site|link)|fake\s+(zerodha|groww|upstox|sebi)\s*(link|site|app)|"
                r"lookalike|phish",
                re.I,
            ),
        ],
    ),
    (
        "fake_sebi_claim",
        'Unverified "SEBI registered" marketing claim',
        'बिना जाँच "SEBI रजिस्टर्ड" का दावा',
        [
            re.compile(
                r"sebi[\s\-]?registered|sebi[\s\-]?verified|registered\s+(with|by)\s+sebi|"
                r"sebi\s+approved|licensed\s+by\s+sebi",
                re.I,
            ),
            re.compile(
                r"सेबी\s*(से\s*)?(रजिस्टर्ड|पंजीकृत|वेरिफाइड|मान्यताप्राप्त|अप्रूव्ड)|"
                r"SEBI\s*(रजिस्टर्ड|पंजीकृत)",
            ),
            re.compile(
                r"sebi\s+(se\s+)?(registered|verified|approved)|sebi\s+wala\s+advisor|"
                r"registered\s+advisor\s+sebi",
                re.I,
            ),
        ],
    ),
    (
        "impersonating_official",
        "Impersonating SEBI / exchange / government officials",
        "SEBI / एक्सचेंज / सरकारी अधिकारी होने का दावा",
        [
            re.compile(
                r"(i\s+am|this\s+is).{0,20}(sebi|nse|bse|rbi|cbi|ed)\s+(officer|official|inspector)|"
                r"(sebi|nse|bse|rbi)\s+(officer|official|inspector)|from\s+sebi\s+(office|headquarters)",
                re.I,
            ),
            re.compile(
                r"(मैं|हम)\s*(सेबी|SEBI|NSE|BSE|RBI|सीबीआई|ईडी).{0,10}(अधिकारी|ऑफिसर|इंस्पेक्टर)|"
                r"(सेबी|NSE|BSE)\s*(अधिकारी|ऑफिसर)",
            ),
            re.compile(
                r"(main|hum)\s+(sebi|nse|rbi)\s+(officer|official)|sebi\s+officer\s+(bol|baat)|"
                r"government\s+officer\s+(sebi|nse)",
                re.I,
            ),
        ],
    ),
    (
        "insider_operator",
        "Insider / operator / guaranteed circuit claims",
        "अंदरूनी / ऑपरेटर / सर्किट लगने के दावे",
        [
            re.compile(
                r"insider\s+(info|tip|news)|operator\s+(call|game)|circuit\s+(lag|hit|lagi)|"
                r"sure[\s\-]?shot\s+(tip|call)|unpublished\s+price",
                re.I,
            ),
            re.compile(
                r"अंदरूनी\s*(जानकारी|सूचना|टिप)|ऑपरेटर\s*(कॉल|गेम)|सर्किट\s*(लग|लगाएंगे|लगेगा)|"
                r"पक्की\s*टिप|अनपब्लिश्ड",
            ),
            re.compile(
                r"andarooni|insider\s+(tip|info)|operator\s+call|circuit\s+lagayenge|"
                r"pakki\s+tip|sure\s*shot\s+tip",
                re.I,
            ),
        ],
    ),
    (
        "recovery_fee",
        "Recovery-fee / 'we will get your money back' offer",
        "रिकवरी फीस / 'पैसे वापस दिलाएँगे' का प्रस्ताव",
        [
            re.compile(
                r"recover(y)?\s+(your\s+)?(money|funds|losses)|pay\s+(a\s+)?(recovery\s+)?fee|"
                r"get\s+your\s+money\s+back|lost\s+money.{0,30}(fee|pay|agent)",
                re.I,
            ),
            re.compile(
                r"पैसे\s*वापस|नुकसान\s*वापस|रिकवरी\s*(फीस|एजेंट)|धन\s*वापसी\s*(शुल्क|फीस)|"
                r"ठगी\s*वापस",
            ),
            re.compile(
                r"recovery\s+(fee|agent)|paisa\s+wapas|loss\s+recover|"
                r"money\s+back\s+(guarantee|agent|fee)",
                re.I,
            ),
        ],
    ),
    (
        "unsolicited_group_invite",
        "Unsolicited WhatsApp / Telegram / VIP / tip-group invite",
        "बिना माँगे WhatsApp / Telegram / VIP / टिप-ग्रुप आमंत्रण",
        [
            re.compile(
                r"join\s+(our\s+)?((vip|exclusive|premium|paid|private)\s+)?"
                r"((whatsapp|telegram|whats\s*app|tg)\s+)?"
                r"(group|channel|grp|circle)\b|"
                r"add\s+you\s+to\s+(the\s+)?group|free\s+tips?\s+group|"
                r"(vip|exclusive|premium|private)\s+(whatsapp\s+|telegram\s+)?"
                r"(group|grp|circle)|"
                r"whatsapp\s+group\s+link|t\.me/",
                re.I,
            ),
            re.compile(
                r"(व्हाट्सएप|वhatsapp|टेलीग्राम|telegram|वीआईपी|VIP)\s*(ग्रुप|समूह|सर्कल)|"
                r"(प्राइवेट|प्रीमियम|वीआईपी)\s*(सर्कल|ग्रुप|समूह)|"
                r"(हमारे|अपने)\s*(वीआईपी\s*|VIP\s*|प्राइवेट\s*)?(ग्रुप|समूह|सर्कल)|ग्रुप\s*जॉइन|"
                r"मुफ्त\s*टिप\s*ग्रुप|ग्रुप\s*में\s*(आओ|जोड़|जुड़)",
            ),
            re.compile(
                r"whatsapp\s+group\s+(join|link)|telegram\s+(group|channel)\s+join|"
                r"(vip|hamara|apna|private|premium)\s+(group|circle)|"
                r"group\s+join\s+karo|free\s+tip\s+group|grp\s+join",
                re.I,
            ),
        ],
    ),
    (
        "zero_risk_no_loss",
        "Claims of zero risk / no downside / risk-free / no loss",
        "शून्य जोखिम / कोई नुकसान नहीं / रिस्क-फ्री का दावा",
        [
            re.compile(
                r"zero\s+(risk|downside)|no\s+downside|risk[\s\-]?free|no\s+loss(?:es)?\b|"
                r"without\s+(any\s+)?(risk|downside|loss)",
                re.I,
            ),
            re.compile(
                r"शून्य\s*जोखिम|बिना\s*(किसी\s*)?(जोखिम|नुकसान)|जोखिम\s*मुक्त|"
                r"कोई\s*नुकसान\s*नहीं|नो\s*लॉस|रिस्क[\s\-]?फ्री",
            ),
            re.compile(
                r"zero\s+risk|no\s+downside|risk[\s\-]?free|no\s+loss|"
                r"bina\s+(koi\s+)?(nuksaan|risk)|bin\s+risk",
                re.I,
            ),
        ],
    ),
    (
        "capital_multiplier",
        "Multiply / double / triple your capital or money",
        "पूंजी या पैसे को गुणा / दोगुना / तिगुना करने का वादा",
        [
            re.compile(
                r"multipl(?:y|ying)\s+(?:your\s+|members['’]?\s+)?(capital|money|funds|wealth)|"
                r"(double|triple)\s+(your\s+)?(capital|money|funds)|"
                r"capital\s+will\s+(double|triple|multiply)",
                re.I,
            ),
            re.compile(
                r"(पूंजी|पैसा|धन)\s*(को\s*)?(दोगुना|तिगुना|तीन\s*गुना|गुणा)|"
                r"(दोगुना|तिगुना|मल्टीप्लाई)\s*(पूंजी|पैसा|कैपिटल)|"
                r"कैपिटल\s*(दोगुना|मल्टीप्लाई)",
            ),
            re.compile(
                r"multipl(?:y|ying)\s+(members['’]?\s+)?(capital|paisa|money)|"
                r"(double|triple)\s+(your\s+)?(capital|paisa)|"
                r"capital\s+(double|triple|multiply)",
                re.I,
            ),
        ],
    ),
    (
        "dm_for_entry",
        "Asks to DM / message for entry or details",
        "एंट्री या डिटेल के लिए डीएम / मैसेज करने को कहा गया",
        [
            re.compile(
                r"\bdm\s+me\b.{0,40}(entry|details|link)|"
                r"message\s+me.{0,40}(entry|details)|"
                r"\bdm\b.{0,20}(for|to)\s+(the\s+)?(entry|details)|"
                r"dm\s+for\s+(the\s+)?entry",
                re.I,
            ),
            re.compile(
                r"(डीएम|डायरेक्ट\s*मैसेज).{0,20}(एंट्री|डिटेल)|"
                r"मुझे\s*(मैसेज|डीएम).{0,20}(एंट्री|डिटेल)|"
                r"एंट्री.{0,15}(डीएम|मैसेज)",
            ),
            re.compile(
                r"dm\s+(me\s+)?(for|karo).{0,20}(entry|details)|"
                r"message\s+me\s+for\s+(entry|details)|"
                r"entry\s+(ke\s+liye\s+)?dm",
                re.I,
            ),
        ],
    ),
]


_PLACEHOLDERS = ("EMAIL", "UPI", "PHONE", "ID_NUMBER", "IFSC")


def clip_evidence(source: str, start: int, end: int, limit: int = 200) -> str:
    """Slice evidence without cutting a redaction placeholder such as [UPI]."""
    lo = max(0, start)
    hi = min(len(source), max(end, lo + min(limit, max(0, end - start))))
    if hi - lo < limit:
        hi = min(len(source), lo + limit)
    else:
        hi = min(len(source), lo + limit)

    open_idx = source.rfind("[", lo, hi)
    close_idx = source.rfind("]", lo, hi)
    if open_idx != -1 and open_idx > close_idx:
        closer = source.find("]", hi - 1 if hi > 0 else 0)
        if closer != -1:
            hi = closer + 1

    if lo > 0:
        prev_open = source.rfind("[", 0, lo + 1)
        prev_close = source.rfind("]", 0, lo)
        if prev_open != -1 and prev_open > prev_close:
            lo = prev_open

    return source[lo:hi]


def finish_placeholders(snippet: str, source: str | None = None) -> str:
    """If a snippet ends inside [UPI] / [PHONE] / etc., extend it to the closing ]."""
    if not snippet:
        return snippet
    if source and snippet in source:
        idx = source.index(snippet)
        return clip_evidence(source, idx, idx + len(snippet), limit=max(len(snippet), 200))
    if snippet.count("[") <= snippet.count("]"):
        return snippet
    for name in _PLACEHOLDERS:
        token = f"[{name}]"
        for k in range(1, len(token)):
            if snippet.endswith(token[:k]) and not snippet.endswith(token):
                return snippet + token[k:]
    dangling = snippet.rfind("[")
    if dangling != -1 and "]" not in snippet[dangling:]:
        return snippet + "]"
    return snippet


def detect_red_flags(text: str) -> list[RedFlag]:
    flags: list[RedFlag] = []
    seen: set[str] = set()
    for flag_id, label_en, label_hi, patterns in _RULES:
        match: re.Match[str] | None = None
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                break
        if match and flag_id not in seen:
            seen.add(flag_id)
            flags.append(
                RedFlag(
                    id=flag_id,
                    label_en=label_en,
                    label_hi=label_hi,
                    evidence=clip_evidence(text, match.start(), match.end()),
                )
            )
    return flags


def rules_verdict(flags: list[RedFlag]) -> str:
    return "likely_scam" if flags else "no_red_flags_found"


# Guaranteed-return promises and personal-account payment requests dominate risk.
FLAG_WEIGHTS: dict[str, int] = {
    "guaranteed_returns": 42,
    "personal_payment": 42,
    "recovery_fee": 16,
    "remote_access": 14,
    "apk_private_app": 14,
    "impersonating_official": 12,
    "insider_operator": 12,
    "lookalike_broker": 12,
    "fake_sebi_claim": 10,
    "unsolicited_group_invite": 10,
    "zero_risk_no_loss": 22,
    "capital_multiplier": 36,
    "dm_for_entry": 10,
    "urgency_pressure": 8,
}


def risk_score_from_flags(flags: list[RedFlag]) -> int:
    if not flags:
        return 8
    total = sum(FLAG_WEIGHTS.get(flag.id, 10) for flag in flags)
    return min(100, total)


RULE_IDS = [row[0] for row in _RULES]
