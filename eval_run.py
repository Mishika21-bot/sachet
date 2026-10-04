import json
import sys
import time

import httpx

sys.stdout.reconfigure(encoding="utf-8")

from app.redact import redact
from app.rules import detect_red_flags, rules_verdict

API = "https://sachet-rmgt.onrender.com/analyze"

# (language, label, text) with label 1 = scam, 0 = genuine. All synthetic, written by the team.
DATA = [
    # ---- scams, English
    ("en", 1, "Exclusive: our SEBI-registered expert gives 100% sure-shot intraday calls. Pay Rs 2999 for the premium group and recover your losses today."),
    ("en", 1, "Hello, I am a senior analyst from a top broker. Download our private trading app from this link, deposit Rs 10,000 and withdraw Rs 25,000 next week."),
    ("en", 1, "Your demat account will be suspended in 24 hours due to KYC failure. Click this link and enter your details to avoid penalty."),
    ("en", 1, "Last 5 seats! Join our mentorship and our operator will pump the stock tomorrow. Buy before 9:15 and sell at the upper circuit."),
    ("en", 1, "Congratulations! You have won an IPO allotment lottery. Pay the processing fee of Rs 4,500 to receive your shares."),
    ("en", 1, "Sir this is NSDL official, your shares are held up. Share the OTP you received to release them."),
    ("en", 1, "We doubled the money of 300 members this month. Send Rs 20,000 to our company account and see Rs 40,000 in 10 days."),
    ("en", 1, "To recover your lost funds from the earlier broker, pay a refundable verification deposit of Rs 8,000 to our recovery team."),
    # ---- scams, Hindi
    ("hi", 1, "हमारे VIP ग्रुप में जुड़ें, रोज़ाना पक्का मुनाफ़ा, आज ही 3000 रुपये भेजकर सीट बुक करें।"),
    ("hi", 1, "SEBI अधिकारी बोल रहा हूँ, आपका डीमैट खाता बंद होने वाला है। तुरंत यह ऐप डाउनलोड करें और अपना OTP बताएँ।"),
    ("hi", 1, "बिना जोखिम के एक महीने में पैसा दोगुना करें, हमारे ऑपरेटर के साथ सेटअप है, अभी जुड़ें।"),
    ("hi", 1, "आपको प्री-IPO शेयर मिले हैं, अलॉटमेंट के लिए बुकिंग राशि इस निजी खाते में जमा करें।"),
    ("hi", 1, "हमारी कंपनी SEBI से रजिस्टर्ड है, 15 दिन में 50% रिटर्न की गारंटी, पैसा आज ही ट्रांसफर करें।"),
    ("hi", 1, "पुराने ब्रोकर में डूबा पैसा वापस दिलाएँगे, पहले 5000 रुपये फीस जमा कीजिए।"),
    ("hi", 1, "AnyDesk डाउनलोड करें ताकि हमारा एक्सपर्ट आपके फोन से सीधे आपका निवेश ठीक कर सके।"),
    ("hi", 1, "आज रात 9 बजे तक एंट्री लें, कल सुबह शेयर में बड़ा उछाल आएगा, सिर्फ़ हमारे टेलीग्राम ग्रुप को पता है।"),
    # ---- scams, Hinglish
    ("hinglish", 1, "Bhai pakka profit wala tip hai, kal subah tak 2x ho jayega, bas Rs 5000 is UPI pe bhej do."),
    ("hinglish", 1, "Sir aapka demat band hone wala hai, abhi ye link kholke KYC update karo aur OTP share karo."),
    ("hinglish", 1, "Hamare VIP Telegram group me join karo, daily guaranteed returns milte hain, sirf 10 seat bachi hain."),
    ("hinglish", 1, "Operator ka call hai, upper circuit lagega, aaj raat tak entry lo warna chance miss."),
    ("hinglish", 1, "Ye trading app APK download karo, deposit karoge to 30 din me paisa triple."),
    ("hinglish", 1, "Madam apka purana loss recover karwa denge, bas pehle 7000 rupaye verification fee bhejo."),
    ("hinglish", 1, "SEBI registered advisor hu, zero risk plan hai, monthly 25 percent fixed return."),
    ("hinglish", 1, "Screen share karo AnyDesk se, main aapka portfolio theek kar deta hu, bas code bata do."),
    # ---- genuine, English
    ("en", 0, "Your SIP of Rs 2,000 for the month has been processed. Units will be allotted at the applicable NAV."),
    ("en", 0, "Reminder: mutual fund investments are subject to market risks. Read all scheme related documents carefully."),
    ("en", 0, "Your demat account statement for September is now available in the official app. Never share your OTP with anyone."),
    ("en", 0, "NSDL has launched a new feature to track nominee details. Visit the official website to learn more."),
    ("en", 0, "What does diversification mean and why do financial planners recommend it?"),
    ("en", 0, "The IPO of a company opens for subscription tomorrow. Retail investors can apply through UPI using their broker application."),
    ("en", 0, "Your fixed deposit of Rs 50,000 will mature next week at the interest rate agreed when you opened it."),
    ("en", 0, "SEBI has advised investors to verify the registration of any adviser on the official SEBI website before investing."),
    # ---- genuine, Hindi
    ("hi", 0, "आपका मासिक SIP सफलतापूर्वक हो गया है। यूनिट्स लागू NAV पर आवंटित की जाएँगी।"),
    ("hi", 0, "म्यूचुअल फंड निवेश बाज़ार जोखिमों के अधीन हैं। कृपया निवेश से पहले सभी योजना दस्तावेज़ ध्यान से पढ़ें।"),
    ("hi", 0, "अपना OTP कभी किसी के साथ साझा न करें, चाहे वह खुद को बैंक या ब्रोकर का कर्मचारी बताए।"),
    ("hi", 0, "SIP क्या होता है और छोटे निवेशकों के लिए यह कैसे उपयोगी हो सकता है?"),
    ("hi", 0, "डीमैट खाते में नॉमिनी जोड़ने के लिए अपने डिपॉजिटरी की आधिकारिक वेबसाइट देखें।"),
    ("hi", 0, "आपकी एफडी अगले सप्ताह परिपक्व हो रही है। ब्याज दर वही रहेगी जो खाता खोलते समय तय हुई थी।"),
    ("hi", 0, "शिकायत दर्ज करने के लिए SEBI की SCORES वेबसाइट का उपयोग करें।"),
    ("hi", 0, "बाज़ार आज मामूली गिरावट के साथ बंद हुआ। निवेशकों को लंबी अवधि का नज़रिया रखने की सलाह दी जाती है।"),
    # ---- genuine, Hinglish
    ("hinglish", 0, "Aapka monthly SIP ho gaya hai, units NAV ke hisaab se allot honge."),
    ("hinglish", 0, "Mutual fund me invest karne se pehle scheme ke documents dhyan se padhein, market risk hota hai."),
    ("hinglish", 0, "Kisi ko bhi apna OTP mat batao, chahe wo khud ko bank wala bataye."),
    ("hinglish", 0, "Diversification ka matlab kya hota hai, simple example ke saath samjhao."),
    ("hinglish", 0, "Nominee add karna ho to apne depository ki official website par jao."),
    ("hinglish", 0, "Aapki FD agle hafte mature ho rahi hai, interest rate wahi rahega jo shuru me tay hua tha."),
    ("hinglish", 0, "SCORES par complaint kaise file karte hain, step by step bata do."),
    ("hinglish", 0, "Aaj market thoda neeche band hua, long term investors ke liye ghabrane ki zarurat nahi."),
]


def run_rules(text, lang):
    flags = detect_red_flags(redact(text))
    return {"verdict": rules_verdict(flags), "mode": "rules_only", "secs": 0.0}


def run_live(text, lang):
    t = time.monotonic()
    for attempt in range(2):
        try:
            r = httpx.post(API, json={"text": text, "lang": lang}, timeout=60)
            r.raise_for_status()
            d = r.json()
            return {"verdict": d["verdict"], "mode": d["analysis_mode"], "secs": time.monotonic() - t}
        except Exception as exc:
            err = type(exc).__name__
            time.sleep(8)
    return {"verdict": "error", "mode": err, "secs": time.monotonic() - t}


def pct(n, d):
    return "n/a" if d == 0 else f"{100 * n / d:.0f}%"


def summarize(rows):
    print(f"\n{'group':10} {'scams':>5} {'legit':>5} | {'scam caught':>11} {'strict caught':>13} | {'legit warned':>12} {'legit flagged scam':>18}")
    for key in ["en", "hi", "hinglish", "ALL"]:
        sub = [r for r in rows if key == "ALL" or r["lang"] == key]
        s = [r for r in sub if r["label"] == 1]
        g = [r for r in sub if r["label"] == 0]
        caught = sum(r["verdict"] not in ("no_red_flags_found", "error") for r in s)
        strict = sum(r["verdict"] == "likely_scam" for r in s)
        warned = sum(r["verdict"] not in ("no_red_flags_found", "error") for r in g)
        flagged = sum(r["verdict"] == "likely_scam" for r in g)
        print(f"{key:10} {len(s):>5} {len(g):>5} | {pct(caught, len(s)):>11} {pct(strict, len(s)):>13} | {pct(warned, len(g)):>12} {pct(flagged, len(g)):>18}")
    tp = sum(r["label"] == 1 and r["verdict"] not in ("no_red_flags_found", "error") for r in rows)
    fp = sum(r["label"] == 0 and r["verdict"] not in ("no_red_flags_found", "error") for r in rows)
    print(f"\nPrecision (any warning on a scam / all warnings): {pct(tp, tp + fp)}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "rules"
    rows = []
    for i, (lang, label, text) in enumerate(DATA, 1):
        res = run_rules(text, lang) if mode == "rules" else run_live(text, lang)
        rows.append({"i": i, "lang": lang, "label": label, "text": text, **res})
        print(f"{i:02d} {lang:8} {'SCAM ' if label else 'LEGIT'} -> {res['verdict']:20} {res['mode']}  {res['secs']:.1f}s", flush=True)
        if mode == "live":
            time.sleep(6)
    summarize(rows)
    if mode == "live":
        modes = {}
        for r in rows:
            modes[r["mode"]] = modes.get(r["mode"], 0) + 1
        print("\nAnalysis modes:", modes)
    print("\nMISSED SCAMS:")
    for r in rows:
        if r["label"] == 1 and r["verdict"] in ("no_red_flags_found", "error"):
            print(f"  #{r['i']} [{r['lang']}] {r['text'][:70]}")
    print("\nFALSE ALARMS (genuine messages that got any warning):")
    for r in rows:
        if r["label"] == 0 and r["verdict"] not in ("no_red_flags_found", "error"):
            print(f"  #{r['i']} [{r['lang']}] {r['verdict']}: {r['text'][:70]}")
    with open(f"eval_results_{mode}.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


main()