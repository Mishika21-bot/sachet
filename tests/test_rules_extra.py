import pytest

from app.rules import detect_red_flags

CASES = [
    ("otp_request", "Please share the OTP you just received to complete verification."),
    ("otp_request", "अपना ओटीपी बताओ ताकि हम आपका खाता वेरिफाई कर सकें।"),
    ("otp_request", "Sir apna OTP batao, abhi verify karna hai."),
    ("account_suspension_link", "Your demat account will be suspended today. Click the link and update KYC."),
    ("account_suspension_link", "आपका डीमैट खाता बंद हो जाएगा, तुरंत लिंक खोलकर केवाईसी अपडेट करें।"),
    ("account_suspension_link", "Aapka demat account band ho jayega, abhi link par KYC update karo."),
    ("advance_fee", "Pay the processing fee of Rs 4500 to receive your shares."),
    ("advance_fee", "रजिस्ट्रेशन फीस के रूप में पहले पाँच हज़ार रुपये जमा करें।"),
    ("advance_fee", "Pehle registration fees bhejo phir paisa wapas milega."),
    ("pump_operator", "Our operator will pump this stock tomorrow morning."),
    ("pump_operator", "हमारा ऑपरेटर कल यह शेयर उछाल देगा।"),
    ("pump_operator", "Operator ka setup ready hai, kal pump hoga."),
    ("member_returns_claim", "We doubled the money of 300 members this month."),
    ("member_returns_claim", "हमने अपने सदस्यों का पैसा दोगुना कर दिया है।"),
    ("member_returns_claim", "Humne members ka paisa double kar diya."),
    ("unofficial_trading_app", "Download our private trading app and start earning."),
]

SAFE = [
    ("otp_request", "Your OTP for logging in is 482913. Do not share it with anyone, including our staff."),
    ("otp_request", "Never share your OTP with anyone."),
    ("otp_request", "अपना ओटीपी किसी से साझा न करें।"),
    ("otp_request", "Kisi ko bhi apna OTP mat batao."),
    ("account_suspension_link", "Dividend of Rs 3.50 per share has been credited to your bank account."),
    ("advance_fee", "Your SIP of Rs 2000 for the month has been processed."),
]


@pytest.mark.parametrize("flag_id,text", CASES)
def test_extra_rule_fires(flag_id: str, text: str) -> None:
    assert flag_id in {f.id for f in detect_red_flags(text)}


@pytest.mark.parametrize("flag_id,text", SAFE)
def test_extra_rule_stays_quiet_on_genuine(flag_id: str, text: str) -> None:
    assert flag_id not in {f.id for f in detect_red_flags(text)}