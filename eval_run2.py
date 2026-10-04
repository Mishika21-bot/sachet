import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

from app.redact import redact
from app.rules import detect_red_flags, rules_verdict

API = "https://sachet-rmgt.onrender.com/analyze"

# (language, label, text); label 1 = scam, 0 = genuine. Synthetic, held out: do not tune on these.
DATA2 = [
    ("en", 1, "Bro my uncle works at a Dubai fund and taught me this platform. I made 3 lakh last month. I will guide you step by step, just open an account on the app I send."),
    ("en", 1, "Unclaimed dividend of Rs 48,200 is pending in your name at IEPF. Pay the Rs 1,850 tax clearance first and we will release it to your bank."),
    ("en", 1, "Watch this video of a famous finance expert explaining the secret AI trading bot. Link in bio, limited slots, join today and let the bot trade for you."),
    ("en", 1, "Dear investor, SEBI has approved our scheme for retail investors. Fixed monthly payout of 6 percent on your capital, withdraw anytime. Call our relationship manager on WhatsApp."),
    ("en", 1, "Your IPO application has been selected for special quota. Confirm by paying Rs 12,000 through the link, otherwise the allotment will be cancelled."),
    ("en", 1, "I am sending a code to your phone for my verification, please read it out to me so I can confirm your demat nomination."),
    ("en", 1, "Our team will manage your trading account on your behalf. Just give us your login and password, you only keep the profit."),
    ("en", 1, "Join our paid webinar. Every attendee gets a free sure tip that gave 80 percent gains this week. Register with Rs 499 now."),
    ("hi", 1, "आपके नाम पर पुराने शेयर का पैसा अटका है। इसे निकालने के लिए पहले टैक्स के नाम पर 2500 रुपये इस लिंक पर भेजिए।"),
    ("hi", 1, "नमस्ते, मैं निवेश सलाहकार हूँ। हमारा एआई सॉफ़्टवेयर हर हफ़्ते 20 प्रतिशत कमाई कराता है। पहले 10 हज़ार से खाता खोलिए।"),
    ("hi", 1, "आपका केवाईसी अधूरा है, आज रात तक यह लिंक खोलकर अपना पैन और आधार नंबर भरें वरना डीमैट खाता रोक दिया जाएगा।"),
    ("hi", 1, "हमारे साथ जुड़िए, आपका लगाया पैसा 45 दिन में तीन गुना होगा। पैसा सीधे हमारे मैनेजर के खाते में भेजिए।"),
    ("hi", 1, "आपको नकद इनाम मिला है। इसे पाने के लिए अपने बैंक का पिन और कार्ड के पीछे का नंबर बताइए।"),
    ("hi", 1, "सेबी से जुड़े अधिकारी आपसे बात करेंगे। आपके खाते में गड़बड़ी है। कॉल पर बने रहिए और जो ऐप बताएँ वह डाउनलोड कर लीजिए।"),
    ("hinglish", 1, "Bhai ye new coin 10 din me 5x hoga, mere cousin ko pata hai. Pehle thoda amount is wallet me daal do, baad me bada karenge."),
    ("hinglish", 1, "Madam aapka refund ruka hua hai SEBI ke paas. Release karwane ke liye 3000 ki fees pehle bhej dijiye, fir paisa turant aa jayega."),
    ("hinglish", 1, "Free demo class hai kal, wahan live trade karwayenge aur jo bhi follow karega uska profit pakka. Bas Rs 999 registration jama kar do."),
    ("hinglish", 1, "Sir mera naam Rohit hai, main broker office se bol raha hu. Aapke account me issue hai, aap mujhe screen dikhao app se, phir main theek kar dunga."),
    ("hinglish", 1, "Is group me daily 3 call milti hai, har call me kam se kam 20 percent. Fees sirf 5000, aaj admission band hone wala hai."),
    ("hinglish", 1, "Aapko ek exclusive IPO pre-booking ka chance mila hai, 100 log hi lenge. Bank details aur OTP bhejo, hum slot lock kar denge."),
    ("en", 0, "Your OTP for logging in to your trading app is 482913. Do not share it with anyone, including our staff. Valid for 5 minutes."),
    ("en", 0, "Allotment status for the IPO you applied for is now available on the registrar's website. Refunds for non allotted applications are credited to your bank account within the stipulated timeline."),
    ("en", 0, "Scam alert: fraudsters are posing as brokers and asking for OTPs. Never share OTPs or install remote access apps. Report fraud on 1930."),
    ("en", 0, "Your mutual fund statement for the quarter is attached. For queries please contact the registered AMC or visit the official website."),
    ("en", 0, "Hi, my colleague told me about a stock tip group offering guaranteed returns. Do you think it is a scam? How can I check?"),
    ("en", 0, "The central bank announced a change in the repo rate today. Fixed deposit rates may change in the coming weeks."),
    ("en", 0, "Your nominee details have been updated successfully in your demat account. If you did not request this change, contact your depository participant."),
    ("en", 0, "Dividend of Rs 3.50 per share has been credited to your bank account linked to your demat account."),
    ("hi", 0, "आपके डीमैट खाते का मासिक विवरण उपलब्ध है। कृपया आधिकारिक ऐप में लॉग इन करके देखें। अपना ओटीपी किसी से साझा न करें।"),
    ("hi", 0, "सावधान रहें: कोई भी अधिकारी फ़ोन पर आपसे ओटीपी या रिमोट ऐप नहीं माँगता। संदिग्ध कॉल की सूचना 1930 पर दें।"),
    ("hi", 0, "म्यूचुअल फंड में एसआईपी बाज़ार के उतार-चढ़ाव में औसत लागत घटाने में मदद करता है, पर इसमें रिटर्न की कोई गारंटी नहीं होती।"),
    ("hi", 0, "आईपीओ के लिए आवेदन करने की अंतिम तारीख कल है। आवेदन अपने ब्रोकर ऐप या बैंक की यूपीआई सुविधा से करें।"),
    ("hi", 0, "आपकी एफडी पर ब्याज अब हर तिमाही आपके बचत खाते में जमा होगा।"),
    ("hi", 0, "अगर आपके साथ ठगी हुई है तो तुरंत अपने बैंक और साइबर क्राइम हेल्पलाइन 1930 से संपर्क करें।"),
    ("hinglish", 0, "Aapka SIP is mahine ka 5th ko debit hoga, balance rakhein warna instalment fail ho sakta hai."),
    ("hinglish", 0, "Market aaj upar band hua, lekin long term investors ko daily movement par jyada dhyaan dene ki zarurat nahi."),
    ("hinglish", 0, "Kisi bhi unknown link par KYC update mat karo, hamesha official app ya website se hi karo."),
    ("hinglish", 0, "Aapka demat account ka annual maintenance charge agle mahine debit hoga, details ke liye official app dekhein."),
    ("hinglish", 0, "Dividend aapke bank account me credit ho gaya hai, statement me check kar sakte hain."),
    ("hinglish", 0, "SEBI ne naye investors ke liye awareness campaign shuru kiya hai, details unki official website par hain."),
]


def live(text, lang):
    for _ in range(2):
        try:
            r = httpx.post(API, json={"text": text, "lang": lang}, timeout=60)
            r.raise_for_status()
            d = r.json()
            return d["verdict"], d["analysis_mode"]
        except Exception:
            time.sleep(8)
    return "error", "error"


def warned(verdict):
    return verdict not in ("no_red_flags_found", "error")


def main():
    rows = []
    for i, (lang, label, text) in enumerate(DATA2, 1):
        rv = rules_verdict(detect_red_flags(redact(text)))
        fv, mode = live(text, lang)
        rows.append((i, lang, label, rv, fv, mode, text))
        print(f"{i:02d} {lang:8} {'SCAM ' if label else 'LEGIT'} rules={rv:20} full={fv:20} {mode}", flush=True)
        time.sleep(6)

    scams = [r for r in rows if r[2] == 1]
    legit = [r for r in rows if r[2] == 0]
    for name, idx in (("RULES ONLY", 3), ("FULL SYSTEM", 4)):
        caught = sum(warned(r[idx]) for r in scams)
        strict = sum(r[idx] == "likely_scam" for r in scams)
        alarms = sum(warned(r[idx]) for r in legit)
        print(f"\n{name}: scams warned {caught}/{len(scams)} (likely_scam {strict}/{len(scams)}); genuine warned {alarms}/{len(legit)}")

    modes = {}
    for r in rows:
        modes[r[5]] = modes.get(r[5], 0) + 1
    print("\nAnalysis modes:", modes)

    print("\nMISSED BY FULL SYSTEM:")
    for r in scams:
        if not warned(r[4]):
            print(f"  #{r[0]} [{r[1]}] {r[6][:70]}")
    print("\nFALSE ALARMS BY FULL SYSTEM:")
    for r in legit:
        if warned(r[4]):
            print(f"  #{r[0]} [{r[1]}] {r[4]}: {r[6][:70]}")


main()