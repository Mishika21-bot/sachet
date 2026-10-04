"""Extra scam-pattern rules (English / Hindi / Hinglish). Loaded by app/rules.py."""

from __future__ import annotations

import re

_FLAGS = re.I | re.S

EXTRA_RULES: list[tuple[str, str, str, list[re.Pattern[str]]]] = [
    (
        "otp_request",
        "Asks you to share an OTP / PIN / CVV",
        "OTP / पिन / CVV साझा करने को कहा गया",
        [
            re.compile(
                r"\A(?!.*\b(?:never|do\s+not|don'?t|dont|won'?t|will\s+not|not\s+to)\b)"
                r".*?\b(?:share|send|tell|give|provide|forward|read\s+out)\s+"
                r"(?:me\s+|us\s+)?(?:the\s+|your\s+|that\s+)?(?:otp|one[\s\-]?time\s+password|pin|cvv)\b",
                _FLAGS,
            ),
            re.compile(
                r"\A(?!.*(?:कभी|न\s*करें|मत\s*(?:बताएँ|बताएं|दें|करें)|नहीं)).*?"
                r"(?:OTP|ओटीपी|पिन)\s*(?:बताओ|बताइए|बताएँ|बताएं|दो|दीजिए|भेजो|भेजिए|शेयर\s*करो|शेयर\s*करें)",
                _FLAGS,
            ),
            re.compile(
                r"\A(?!.*\b(?:mat|never|nahi|nahin)\b).*?"
                r"\botp\s+(?:batao|bata\s+do|bhejo|bhej\s+do|dedo|de\s+do|do|share\s+kar(?:o|na))\b",
                _FLAGS,
            ),
        ],
    ),
    (
        "account_suspension_link",
        "Threat to suspend / block your account unless you click, verify or update",
        "खाता बंद / ब्लॉक करने की धमकी और लिंक / KYC / वेरिफिकेशन की माँग",
        [
            re.compile(
                r"\b(?:account|demat|kyc)\b.{0,60}\b(?:suspend\w*|block\w*|freez\w*|frozen|clos(?:e|ed|ure)|deactivat\w*)\b"
                r".{0,100}\b(?:click|tap|link|kyc|verify|update|otp|download)\b",
                _FLAGS,
            ),
            re.compile(
                r"(?:खाता|खाते|अकाउंट|डीमैट).{0,40}(?:बंद|ब्लॉक|फ्रीज|सस्पेंड|निलंबित)"
                r".{0,80}(?:लिंक|केवाईसी|KYC|ओटीपी|OTP|डाउनलोड|वेरिफ|अपडेट)",
                _FLAGS,
            ),
            re.compile(
                r"\b(?:account|demat|kyc)\b.{0,40}\b(?:band|block|freeze|frozen|suspend\w*)\b"
                r".{0,80}\b(?:link|kyc|otp|verify|update|download)\b",
                _FLAGS,
            ),
        ],
    ),
    (
        "advance_fee",
        "Asks for an upfront fee, deposit or booking amount (including to 'recover' lost money)",
        "पहले फीस / डिपॉज़िट / बुकिंग राशि की माँग (खोया पैसा वापस दिलाने के नाम पर भी)",
        [
            re.compile(
                r"\b(?:pay|send|deposit|transfer)\b.{0,60}\b(?:processing|registration|verification|refundable|release|"
                r"clearance|activation|booking|recovery|security|membership|joining)\s+(?:fees?|charges?|deposit|amount)\b|"
                r"\b(?:won|win|winner)\b.{0,40}\b(?:lottery|lucky\s+draw)\b|"
                r"\brecover\w*\s+(?:your\s+|the\s+)?(?:lost\s+|stolen\s+|stuck\s+)?(?:money|funds|losses|capital|amount)\b"
                r".{0,100}\b(?:fees?|pay|deposit|charges?)\b",
                _FLAGS,
            ),
            re.compile(
                r"(?:प्रोसेसिंग|रजिस्ट्रेशन|वेरिफिकेशन|रिफंडेबल|बुकिंग|रिकवरी|सिक्योरिटी|क्लीयरेंस)\s*"
                r"(?:फीस|शुल्क|डिपॉज़िट|डिपॉजिट|चार्ज)|"
                r"(?:निजी|पर्सनल)\s*(?:खाते|खाता|अकाउंट|यूपीआई|UPI)|"
                r"(?:पहले|एडवांस).{0,30}(?:फीस|शुल्क).{0,20}(?:जमा|भेज)|"
                r"(?:पैसा|पैसे|रकम)\s*वापस.{0,80}(?:फीस|शुल्क|जमा)|"
                r"डूबा\s*(?:हुआ\s*)?पैसा",
                _FLAGS,
            ),
            re.compile(
                r"\b(?:processing|registration|verification|refundable|booking|recovery|security|clearance)\s+"
                r"(?:fees?|charges?|deposit)\b|"
                r"\b(?:pehle|advance)\b.{0,30}\b(?:fees?|charges?)\b.{0,20}\b(?:bhejo|bhej|jama|do)\b|"
                r"\b(?:paisa|paise)\s+wapas\b.{0,80}\b(?:fees?|bhejo|jama)\b",
                _FLAGS,
            ),
        ],
    ),
    (
        "pump_operator",
        "'Operator will pump the stock' / buy-before-the-jump style call",
        "'ऑपरेटर शेयर उछालेगा' / कल उछाल आएगा जैसा दावा",
        [
            re.compile(
                r"\boperator\b.{0,60}\b(?:will|pump|circuit)\b|\bwill\s+pump\b|"
                r"\bbuy\s+before\b.{0,40}\bsell\s+(?:at|on)\b|"
                r"\bupper\s+circuit\b.{0,80}\b(?:tomorrow|tonight|guarantee\w*|sure[\s\-]?shot)\b",
                _FLAGS,
            ),
            re.compile(
                r"ऑपरेटर.{0,40}(?:पंप|सर्किट|उछाल)|"
                r"कल\s*(?:सुबह\s*)?(?:शेयर|स्टॉक).{0,30}(?:उछाल|अपर\s*सर्किट|ऊपरी\s*सर्किट)",
                _FLAGS,
            ),
            re.compile(
                r"\boperator\b.{0,40}\b(?:setup|pump|circuit|lagayega|lagayenge)\b|"
                r"\bupper\s+circuit\b.{0,40}\b(?:lagega|lagayenge|kal|aaj\s+raat)\b",
                _FLAGS,
            ),
        ],
    ),
    (
        "member_returns_claim",
        "Claims about doubling members' money, or 'send X, get 2X' offers",
        "सदस्यों का पैसा दोगुना करने या 'X भेजो, 2X पाओ' का दावा",
        [
            re.compile(
                r"\b(?:doubled|tripled|multiplied)\b.{0,40}\b(?:money|capital|funds)\b.{0,40}"
                r"\b(?:members|clients|investors|followers|people|subscribers)\b|"
                r"\b(?:send|invest|deposit|transfer)\b.{0,15}(?:rs\.?|inr|₹)\s*[\d,]+.{0,80}"
                r"\b(?:see|get|receive|earn|withdraw)\b.{0,15}(?:rs\.?|inr|₹)\s*[\d,]+",
                _FLAGS,
            ),
            re.compile(
                r"(?:सदस्यों|मेंबर्स|क्लाइंट्स|निवेशकों).{0,30}(?:पैसा|पैसे|पूंजी).{0,20}(?:दोगुना|डबल)|"
                r"(?:दोगुना|डबल).{0,30}(?:सदस्यों|मेंबर्स)",
                _FLAGS,
            ),
            re.compile(
                r"\bmembers\s+ka\s+(?:paisa|paise|capital)\b.{0,20}\b(?:double|triple)\b",
                _FLAGS,
            ),
        ],
    ),
    (
        "unofficial_trading_app",
        "Asks you to download a private trading app and deposit money",
        "निजी ट्रेडिंग ऐप डाउनलोड करवाकर पैसा जमा करवाने की कोशिश",
        [
            re.compile(
                r"\bprivate\s+(?:trading|investment|investing)\s+app\b|"
                r"\b(?:download|install)\b\s+our\s+(?:\w+\s+){0,3}app\b.{0,160}\b(?:deposit|withdraw)\b",
                _FLAGS,
            ),
        ],
    ),
]

EXTRA_WEIGHTS: dict[str, int] = {
    "otp_request": 40,
    "account_suspension_link": 30,
    "advance_fee": 40,
    "pump_operator": 25,
    "member_returns_claim": 30,
    "unofficial_trading_app": 22,
}