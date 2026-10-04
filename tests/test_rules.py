import pytest

from app.rules import RULE_IDS, detect_red_flags

SAMPLES: dict[str, dict[str, str]] = {
    "guaranteed_returns": {
        "en": "Guaranteed returns and risk-free profit this month.",
        "hi": "गारंटीड रिटर्न और पक्का मुनाफा मिलेगा।",
        "hinglish": "Is scheme me pakka profit aur double paisa hai.",
    },
    "urgency_pressure": {
        "en": "Act now, last chance, limited seats only.",
        "hi": "आज ही निवेश करो, यह आखिरी मौका है।",
        "hinglish": "Jaldi karo, aaj hi invest karna hai.",
    },
    "personal_payment": {
        "en": "Pay to my personal UPI right now.",
        "hi": "पैसे मेरे यूपीआई पर भेजो।",
        "hinglish": "Mere upi pe paise bhejo instantly.",
    },
    "apk_private_app": {
        "en": "Download this APK, it is not on Play Store.",
        "hi": "यह एपीके डाउनलोड करो, प्ले स्टोर से नहीं मिलेगा।",
        "hinglish": "Private app apk download karo, Play Store se nahi hai.",
    },
    "remote_access": {
        "en": "Install AnyDesk so I can take remote access.",
        "hi": "एनीडेस्क लगाओ, रिमोट एक्सेस चाहिए।",
        "hinglish": "TeamViewer se remote access de do.",
    },
    "lookalike_broker": {
        "en": "Open the trading app at zerodhaa.xyz today.",
        "hi": "यह नकली ब्रोकर वेबसाइट खोलो।",
        "hinglish": "Yeh fake zerodha link mat use karna.",
    },
    "fake_sebi_claim": {
        "en": "I am a SEBI registered advisor, fully licensed by SEBI.",
        "hi": "मैं सेबी रजिस्टर्ड सलाहकार हूँ।",
        "hinglish": "Main sebi se registered advisor hoon.",
    },
    "impersonating_official": {
        "en": "This is SEBI officer calling from headquarters.",
        "hi": "मैं सेबी अधिकारी हूँ, अभी बात करो।",
        "hinglish": "Main sebi officer bol raha hoon.",
    },
    "insider_operator": {
        "en": "Insider tip from operator call, circuit will hit.",
        "hi": "अंदरूनी जानकारी है, ऑपरेटर कॉल पर सर्किट लगेगा।",
        "hinglish": "Operator call hai, pakki tip, circuit lagayenge.",
    },
    "recovery_fee": {
        "en": "Pay a recovery fee to get your money back.",
        "hi": "रिकवरी फीस दो, पैसे वापस दिलाएँगे।",
        "hinglish": "Recovery fee do, paisa wapas mil jayega.",
    },
    "unsolicited_group_invite": {
        "en": "Join our WhatsApp group for free tips.",
        "hi": "हमारा व्हाट्सएप ग्रुप जॉइन करो।",
        "hinglish": "Telegram group join karo, free tip group hai.",
    },
    "zero_risk_no_loss": {
        "en": "This trade has zero risk and no downside.",
        "hi": "इसमें शून्य जोखिम है, कोई नुकसान नहीं।",
        "hinglish": "Bhai zero risk hai, no loss guaranteed scheme nahi yeh sirf no downside.",
    },
    "capital_multiplier": {
        "en": "We have been multiplying members' capital every month.",
        "hi": "हम आपकी पूंजी को दोगुना करते हैं।",
        "hinglish": "Yahan capital multiply hota hai har mahine.",
    },
    "dm_for_entry": {
        "en": "DM me for the entry window and details.",
        "hi": "एंट्री के लिए मुझे डीएम करो डिटेल भेजूँगा।",
        "hinglish": "Entry ke liye dm karo details dunga.",
    },
}

VIP_SCAM = (
    "Join our VIP group! Guaranteed 40% returns in 15 days. "
    "Pay Rs 5000 to 98xxxxxx@upi now, limited seats!"
)


def test_guaranteed_returns_allows_percent_in_between() -> None:
    samples = [
        "Guaranteed 40% returns in 15 days",
        "Assured 20% profit this week",
        "Fixed returns with no risk",
        "Sure-shot returns for members",
        "गारंटीड 40% रिटर्न मिलेगा",
        "आश्वस्त मुनाफा 20% है",
        "Assured 30% munafa pakka hai",
        "Sure shot 15% profit",
    ]
    for text in samples:
        hits = {flag.id for flag in detect_red_flags(text)}
        assert "guaranteed_returns" in hits, text


def test_vip_group_invite_without_whatsapp_name() -> None:
    hits = {flag.id for flag in detect_red_flags("Join our VIP group!")}
    assert "unsolicited_group_invite" in hits


def test_classic_vip_payment_message_hits_core_flags() -> None:
    hits = {flag.id for flag in detect_red_flags(VIP_SCAM)}
    assert "guaranteed_returns" in hits
    assert "unsolicited_group_invite" in hits
    assert "personal_payment" in hits
    assert "urgency_pressure" in hits


PRIVATE_CIRCLE = (
    "Our senior analyst's private circle has been multiplying members' capital "
    "every month with zero downside. DM me for the entry window."
)


def test_private_circle_multiplier_message_is_likely_scam() -> None:
    hits = {flag.id for flag in detect_red_flags(PRIVATE_CIRCLE)}
    assert "unsolicited_group_invite" in hits
    assert "capital_multiplier" in hits
    assert "zero_risk_no_loss" in hits
    assert "dm_for_entry" in hits


@pytest.mark.parametrize("flag_id", RULE_IDS)
@pytest.mark.parametrize("lang", ["en", "hi", "hinglish"])
def test_each_rule_fires_in_all_languages(flag_id: str, lang: str) -> None:
    text = SAMPLES[flag_id][lang]
    hits = {flag.id for flag in detect_red_flags(text)}
    assert flag_id in hits, f"{flag_id} did not fire for {lang}: {text!r} got {hits}"
