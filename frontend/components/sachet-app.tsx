'use client'

import { useMemo, useState } from 'react'
import { AlertTriangle, ArrowLeft, Check, CircleStop, Headphones, Mic, ShieldCheck, Sparkles, Volume2 } from 'lucide-react'

const LANGUAGES = [
  { value: 'hi', label: 'हिन्दी' },
  { value: 'en', label: 'English' },
  { value: 'hinglish', label: 'Hinglish' },
] as const

type Language = (typeof LANGUAGES)[number]['value']
type Screen = 'check' | 'result' | 'pause' | 'sent'
type Verdict = 'likely_scam' | 'uncertain' | 'no_red_flags_found'

type Confidence = 'low' | 'medium' | 'high'

type Flag = { label?: string; label_en?: string; label_hi?: string; label_hinglish?: string; evidence: string }

type Analysis = {
  verdict: Verdict
  risk_score: number
  confidence?: Confidence
  red_flags: Flag[]
  explanation: string
  next_steps: string[]
  disclaimer: string
  analysis_mode?: string
}

const copy = {
  en: {
    eyebrow: 'Sachet · सचेत',
    tagline: 'A quiet second look before you trust a message.',
    prompt: 'Paste the message you received',
    placeholder: 'Paste a WhatsApp message, SMS, email, or call transcript here…',
    check: 'Check this message',
    checking: 'Checking carefully…',
    listen: 'Listen',
    back: 'Check another message',
    pause: 'Pause before you pay',
    pauseIntro: 'Three quick questions can help you slow down and spot pressure.',
    yes: 'Yes',
    no: 'No',
    stop: 'Stop. Do not pay.',
    stopDetail: 'Take a pause. Do not share OTPs, passwords, or send money while you feel rushed.',
    safe: 'No rush is worth your savings.',
    error: 'We could not check that message. Please try again or check your connection.',
    empty: 'Paste a message first so Sachet can look for scam patterns.',
    verdict: { likely_scam: 'Likely scam', uncertain: 'Uncertain', no_red_flags_found: 'No red flags found' },
    risk: 'Risk score', flags: 'What stood out', evidence: 'Evidence', explanation: 'Why this matters', steps: 'What you can do now', mode: 'Analysis mode', disclaimer: 'Sachet spots common warning signs. It cannot guarantee that a message is safe, and it is not financial advice.',
    questions: ['Did someone promise fixed returns?', 'Were you told to hurry?', 'Are you being asked to pay a personal account or install an app?'],
    sentMoney: 'I already sent money', sentTitle: 'If you already sent money', sentSteps: ['Call your bank or UPI app\'s helpline now.', 'Call 1930.', 'Report at cybercrime.gov.in.', 'Keep evidence: screenshots, the UPI ID or number you paid, transaction ID, date and time.', 'Do NOT pay anyone offering to "recover" your money.', 'Never share OTP or PIN.'], sentNote: 'Complaint against a SEBI-registered broker or listed company? Use scores.sebi.gov.in', sentFooter: 'Sachet is not a government service and cannot file complaints, freeze accounts or recover money.', sentBack: 'Back to Sachet',

  },
  hi: {
    eyebrow: 'सचेत · Sachet', tagline: 'किसी संदेश पर भरोसा करने से पहले एक शांत नज़र।', prompt: 'आपको मिला संदेश यहाँ चिपकाएँ', placeholder: 'WhatsApp, SMS, ईमेल या कॉल का संदेश यहाँ चिपकाएँ…', check: 'संदेश जाँचें', checking: 'ध्यान से जाँच रहे हैं…', listen: 'सुनें', back: 'दूसरा संदेश जाँचें', pause: 'पैसे देने से पहले रुकें', pauseIntro: 'जल्दबाज़ी और दबाव को पहचानने के लिए तीन सवाल।', yes: 'हाँ', no: 'नहीं', stop: 'रुकें। पैसे न दें।', stopDetail: 'OTP, पासवर्ड साझा न करें और जल्दबाज़ी में पैसे न भेजें।', safe: 'आपकी बचत से ज़्यादा ज़रूरी कोई जल्दी नहीं।', error: 'संदेश जाँचा नहीं जा सका। फिर कोशिश करें या कनेक्शन जाँचें।', empty: 'पहले कोई संदेश चिपकाएँ ताकि सचेत उसमें धोखाधड़ी के संकेत देख सके।', verdict: { likely_scam: 'धोखाधड़ी की संभावना', uncertain: 'पक्का नहीं', no_red_flags_found: 'कोई स्पष्ट संकेत नहीं' }, risk: 'जोखिम स्कोर', flags: 'क्या दिखा', evidence: 'सबूत', explanation: 'यह क्यों ज़रूरी है', steps: 'अभी आप क्या कर सकते हैं', mode: 'विश्लेषण मोड', disclaimer: 'सचेत आम चेतावनी संकेत दिखाता है। यह संदेश के सुरक्षित होने की गारंटी या वित्तीय सलाह नहीं है।', questions: ['क्या किसी ने पक्के रिटर्न का वादा किया?', 'क्या आपको जल्दी करने को कहा गया?', 'क्या आपसे निजी खाते में पैसे भेजने या कोई ऐप इंस्टॉल करने को कहा गया?'], sentMoney: 'मैंने पैसे भेज दिए हैं', sentTitle: 'अगर आपने पैसे भेज दिए हैं', sentSteps: ['अभी अपने बैंक या UPI ऐप की हेल्पलाइन पर कॉल करें।', '1930 पर कॉल करें।', 'cybercrime.gov.in पर रिपोर्ट करें।', 'सबूत रखें: स्क्रीनशॉट, जिस UPI ID या नंबर पर पैसे भेजे, ट्रांज़ैक्शन ID, तारीख और समय।', 'पैसे "वापस दिलाने" का दावा करने वाले किसी व्यक्ति को पैसे न दें।', 'OTP या PIN कभी साझा न करें।'], sentNote: 'SEBI-रजिस्टर्ड ब्रोकर या सूचीबद्ध कंपनी के खिलाफ शिकायत? scores.sebi.gov.in का उपयोग करें।', sentFooter: 'सचेत सरकारी सेवा नहीं है और शिकायत दर्ज, खाते फ्रीज़ या पैसे वापस नहीं कर सकता।', sentBack: 'सचेत पर वापस जाएँ',
  },
  hinglish: {
    eyebrow: 'Sachet · सचेत', tagline: 'Kisi message par trust karne se pehle ek shaant nazar.', prompt: 'Jo message mila hai, yahan paste karein', placeholder: 'WhatsApp, SMS, email ya call transcript yahan paste karein…', check: 'Message check karein', checking: 'Dhyaan se check kar rahe hain…', listen: 'Sunein', back: 'Doosra message check karein', pause: 'Pay karne se pehle pause karein', pauseIntro: 'Pressure ko pehchanne ke liye teen quick sawaal.', yes: 'Haan', no: 'Nahi', stop: 'Rukiye. Pay mat kijiye.', stopDetail: 'OTP ya password share na karein, aur pressure mein paise na bhejein.', safe: 'Aapki savings se zyada important koi jaldi nahi.', error: 'Message check nahi ho paaya. Dobara try karein ya connection check karein.', empty: 'Pehle message paste karein, tab Sachet scam patterns check karega.', verdict: { likely_scam: 'Scam lag raha hai', uncertain: 'Pakka nahi keh sakte', no_red_flags_found: 'Koi clear red flag nahi' }, risk: 'Risk score', flags: 'Kya dikha', evidence: 'Evidence', explanation: 'Yeh kyun important hai', steps: 'Abhi aap kya kar sakte hain', mode: 'Analysis mode', disclaimer: 'Sachet common warning signs dikhata hai. Yeh safety guarantee ya financial advice nahi hai.', questions: ['Kya kisi ne fixed returns promise kiye?', 'Kya aapko jaldi karne ko kaha gaya?', 'Kya personal account mein pay karne ya koi app install karne ko kaha gaya?'], sentMoney: 'Maine paise bhej diye hain', sentTitle: 'Agar aapne paise bhej diye hain', sentSteps: ['Abhi apne bank ya UPI app ki helpline par call karein.', '1930 par call karein.', 'cybercrime.gov.in par report karein.', 'Evidence sambhal kar rakhein: screenshots, jis UPI ID ya number par pay kiya, transaction ID, date aur time.', 'Paise "recover" karne ka offer dene wale ko pay NA karein.', 'OTP ya PIN kabhi share na karein.'], sentNote: 'SEBI-registered broker ya listed company ke khilaaf complaint? scores.sebi.gov.in use karein.', sentFooter: 'Sachet government service nahi hai aur complaints file, accounts freeze ya paise recover nahi kar sakta.', sentBack: 'Sachet par wapas jaayein',
  },
} satisfies Record<Language, Record<string, any>>

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://127.0.0.1:8000'

export function SachetApp() {
  const [language, setLanguage] = useState<Language>('en')
  const [screen, setScreen] = useState<Screen>('check')
  const [text, setText] = useState('')
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [coolingOff, setCoolingOff] = useState<boolean[]>([false, false, false])
  const t = copy[language]

  const hasStopSignal = coolingOff.some(Boolean)
  const verdictTone = useMemo(() => analysis?.verdict ?? 'uncertain', [analysis])
  const uniqueFlags = useMemo(() => {
    const seenLabels = new Set<string>()
    const seenEvidence = new Set<string>()
    return (analysis?.red_flags ?? []).filter((flag) => {
      const label = (flag.label_en || flag.label || '').trim().toLowerCase()
      const evidence = flag.evidence.trim().toLowerCase()
      if ((label && seenLabels.has(label)) || (evidence && seenEvidence.has(evidence))) return false
      if (label) seenLabels.add(label)
      if (evidence) seenEvidence.add(evidence)
      return true
    })
  }, [analysis?.red_flags])

  function startListening() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) return
    const recognition = new SpeechRecognition()
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN'
    recognition.interimResults = false
    recognition.onresult = (event: any) => setText((current) => `${current}${current ? ' ' : ''}${event.results[0][0].transcript}`)
    recognition.start()
  }

  async function checkMessage() {
    if (!text.trim()) { setError(t.empty); return }
    setLoading(true); setError('')
    try {
      const response = await fetch(`${API_URL}/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: text.trim(), lang: language }) })
      if (!response.ok) throw new Error('Request failed')
      setAnalysis(await response.json())
      setScreen('result')
    } catch { setError(t.error) } finally { setLoading(false) }
  }

  function speak() {
    if (!analysis || !('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(analysis.explanation)
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-IN'
    window.speechSynthesis.speak(utterance)
  }

  return <main className="min-h-screen bg-[#f7f8f5] text-[#18221c]">
    <div className="mx-auto flex min-h-screen w-full max-w-xl flex-col px-5 pb-10 pt-5 sm:px-8">
      <header className="flex items-start justify-between gap-4">
        <button className="text-left" onClick={() => { setScreen('check'); setError('') }} aria-label="Go to home"><span className="block text-xl font-bold tracking-tight">{t.eyebrow}</span><span className="mt-1 block text-xs text-[#637267]">{t.tagline}</span></button>
        <div className="flex rounded-full border border-[#cbd5cb] bg-white p-1" aria-label="Language">
          {LANGUAGES.map((item) => <button key={item.value} onClick={() => setLanguage(item.value)} className={`rounded-full px-2.5 py-1.5 text-xs font-semibold transition ${language === item.value ? 'bg-[#183f2a] text-white' : 'text-[#526158]'}`} aria-pressed={language === item.value}>{item.label}</button>)}
        </div>
      </header>

      <nav className="mt-7 flex gap-2 text-xs font-semibold text-[#607067]" aria-label="Progress"><span className={screen === 'check' ? 'text-[#183f2a]' : ''}>01 Check</span><span>/</span><span className={screen === 'result' ? 'text-[#183f2a]' : ''}>02 Understand</span><span>/</span><span className={screen === 'pause' ? 'text-[#183f2a]' : ''}>03 Pause</span></nav>

      {screen === 'check' && <section className="mt-10 flex flex-1 flex-col"><button onClick={() => setScreen('sent')} className="mb-6 flex min-h-14 w-full items-center justify-center rounded-xl border-2 border-[#a33d38] bg-[#fff0ee] px-5 text-center font-bold text-[#a33d38]">{t.sentMoney}</button><div><div className="mb-3 inline-flex items-center gap-2 rounded-full bg-[#e3eee5] px-3 py-1.5 text-xs font-bold text-[#285739]"><ShieldCheck data-icon="inline-start" /> Private by design</div><h1 className="max-w-md text-4xl font-bold leading-[1.08] tracking-[-0.04em] sm:text-5xl">A second look before you pay.</h1><p className="mt-4 max-w-sm text-base leading-7 text-[#637267]">Sachet looks for common scam patterns in messages sent to Indian investors.</p></div><div className="mt-9 flex flex-col gap-4"><label htmlFor="message" className="text-base font-bold">{t.prompt}</label><div className="relative"><textarea id="message" value={text} onChange={(e) => setText(e.target.value)} placeholder={t.placeholder} className="min-h-48 w-full resize-none rounded-2xl border border-[#cbd5cb] bg-white p-4 pr-14 text-base leading-7 shadow-[0_8px_30px_rgba(40,67,48,0.05)] outline-none placeholder:text-[#89968c] focus:border-[#326744] focus:ring-2 focus:ring-[#b5d0ba]" aria-describedby={error ? 'message-error' : undefined} /><button type="button" onClick={startListening} className="absolute bottom-3 right-3 flex size-11 items-center justify-center rounded-full bg-[#eff4ef] text-[#295a3a] hover:bg-[#dce9de]" aria-label="Use voice input"><Mic /></button></div>{error && <p id="message-error" className="text-sm font-semibold text-[#a52c24]" role="alert">{error}</p>}<button type="button" disabled={loading} onClick={checkMessage} className="flex min-h-14 items-center justify-center gap-2 rounded-xl bg-[#183f2a] px-5 text-base font-bold text-white shadow-[0_8px_20px_rgba(24,63,42,0.18)] transition hover:bg-[#285c3c] disabled:cursor-wait disabled:opacity-70">{loading ? <><Sparkles className="animate-pulse" />{t.checking}</> : <>{t.check}<ArrowLeft className="rotate-180" /></>}</button></div><button onClick={() => setScreen('pause')} className="mt-auto flex items-center justify-between border-t border-[#dbe3dc] pt-5 text-left text-sm font-bold text-[#295a3a]">{t.pause}<span aria-hidden="true">→</span></button></section>}

      {screen === 'result' && analysis && <section className="mt-8 flex flex-col gap-5"><button onClick={() => setScreen('check')} className="flex items-center gap-2 self-start text-sm font-bold text-[#295a3a]"><ArrowLeft />{t.back}</button><button onClick={() => setScreen('sent')} className="flex min-h-14 w-full items-center justify-center rounded-xl border-2 border-[#a33d38] bg-[#fff0ee] px-5 text-center font-bold text-[#a33d38]">{t.sentMoney}</button><div className={`rounded-2xl border p-5 ${verdictTone === 'likely_scam' ? 'border-[#e4aaa4] bg-[#fff0ee]' : verdictTone === 'uncertain' ? 'border-[#e4c98c] bg-[#fff8e8]' : 'border-[#b8d0bc] bg-[#eef7ef]'}`}><div className="flex items-start justify-between gap-4"><div><span className="text-xs font-bold uppercase tracking-widest text-[#637267]">{t.verdict[analysis.verdict]}</span><h1 className="mt-2 flex items-center gap-2 text-3xl font-bold tracking-tight">{verdictTone === 'likely_scam' ? <CircleStop /> : verdictTone === 'uncertain' ? <AlertTriangle /> : <ShieldCheck />}{t.verdict[analysis.verdict]}</h1>{analysis.confidence && <p className="mt-2 text-sm font-semibold text-[#637267]">{language === 'hi' ? `${analysis.confidence === 'low' ? 'कम' : analysis.confidence === 'medium' ? 'मध्यम' : 'उच्च'} भरोसा` : `${analysis.confidence[0].toUpperCase()}${analysis.confidence.slice(1)} confidence`}</p>}</div>{analysis.analysis_mode && <span className="rounded-full bg-white/70 px-2.5 py-1 text-[10px] font-bold text-[#637267]">{analysis.analysis_mode}</span>}</div><div className="mt-6"><div className="mb-2 flex justify-between text-sm font-bold"><span>{t.risk}</span><span>{analysis.risk_score}/100</span></div><div className="h-3 overflow-hidden rounded-full bg-white/70"><div className="h-full rounded-full bg-current transition-all" style={{ width: `${Math.min(100, Math.max(0, analysis.risk_score))}%` }} /></div></div></div><section className="rounded-2xl border border-[#dbe3dc] bg-white p-5"><h2 className="text-lg font-bold">{t.flags}</h2>{uniqueFlags.length ? <ul className="mt-4 flex flex-col gap-4">{uniqueFlags.map((flag, index) => <li key={index} className="border-l-2 border-[#c85a4c] pl-3"><p className="font-bold">{language === 'hi' ? flag.label_hi || flag.label : language === 'hinglish' ? flag.label_hinglish || flag.label : flag.label}</p><p className="mt-1 text-sm leading-6 text-[#637267]">{t.evidence}: "{flag.evidence}"</p></li>)}</ul> : <p className="mt-3 text-sm text-[#637267]">{t.verdict.no_red_flags_found}</p>}</section><section className="rounded-2xl border border-[#dbe3dc] bg-white p-5"><div className="flex items-center justify-between gap-3"><h2 className="text-lg font-bold">{t.explanation}</h2><button onClick={speak} className="flex items-center gap-2 rounded-full bg-[#eff4ef] px-3 py-2 text-sm font-bold text-[#295a3a]"><Volume2 />{t.listen}</button></div><p className="mt-3 leading-7 text-[#46554a]">{analysis.explanation}</p><h2 className="mt-6 text-lg font-bold">{t.steps}</h2><ul className="mt-3 flex flex-col gap-3">{analysis.next_steps.map((step, index) => <li key={index} className="flex gap-3 text-sm leading-6"><Check className="mt-1 shrink-0 text-[#3a7a4c]" />{step}</li>)}</ul></section><p className="px-1 text-xs leading-5 text-[#77847a]">{analysis.disclaimer || t.disclaimer}</p><button onClick={() => setScreen('pause')} className="flex min-h-14 items-center justify-between rounded-xl border border-[#b8d0bc] bg-[#eef7ef] px-5 text-left font-bold text-[#285739]">{t.pause}<span aria-hidden="true">→</span></button></section>}

      {screen === 'sent' && <section className="mt-10 flex flex-1 flex-col gap-5"><div><div className="inline-flex size-14 items-center justify-center rounded-2xl bg-[#fff0ee] text-[#a33d38]"><AlertTriangle /></div><h1 className="mt-6 text-4xl font-bold leading-tight tracking-[-0.04em]">{t.sentTitle}</h1><p className="mt-4 text-base leading-7 text-[#637267]">Act quickly and use only official channels.</p></div><ol className="flex flex-col gap-3" aria-label={t.sentTitle}>{t.sentSteps.map((step: string, index: number) => <li key={step} className="flex gap-3 rounded-2xl border border-[#dbe3dc] bg-white p-4 text-base leading-6"><span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#fff0ee] font-bold text-[#a33d38]">{index + 1}</span><span>{index === 1 ? <a className="font-bold text-[#a33d38] underline" href="tel:1930">{step}</a> : index === 2 ? <span>{step.split('cybercrime.gov.in')[0]}<a className="font-bold text-[#a33d38] underline" href="https://cybercrime.gov.in" target="_blank" rel="noreferrer">cybercrime.gov.in</a>{step.split('cybercrime.gov.in')[1]}</span> : step}</span></li>)}</ol><p className="rounded-xl bg-[#fff8e8] p-4 text-sm font-semibold leading-6 text-[#6c511b]">{t.sentNote.split('scores.sebi.gov.in')[0]}<a className="underline" href="https://scores.sebi.gov.in" target="_blank" rel="noreferrer">scores.sebi.gov.in</a>{t.sentNote.split('scores.sebi.gov.in')[1]}</p><p className="text-xs leading-5 text-[#637267]">{t.sentFooter}</p><button onClick={() => setScreen('check')} className="mt-auto flex min-h-14 items-center justify-center rounded-xl bg-[#183f2a] px-5 font-bold text-white">{t.sentBack}</button></section>}

      {screen === 'pause' && <section className="mt-10 flex flex-1 flex-col"><div className="inline-flex size-14 items-center justify-center rounded-2xl bg-[#e3eee5] text-[#285739]"><ShieldCheck /></div><h1 className="mt-6 text-4xl font-bold leading-tight tracking-[-0.04em]">{t.pause}</h1><p className="mt-4 text-base leading-7 text-[#637267]">{t.pauseIntro}</p><fieldset className="mt-8 flex flex-col gap-4"><legend className="sr-only">{t.pause}</legend>{t.questions.map((question, index) => <div key={question} className="rounded-2xl border border-[#dbe3dc] bg-white p-4"><p className="font-semibold leading-6">{question}</p><div className="mt-4 flex gap-2">{[true, false].map((value) => <button key={String(value)} onClick={() => setCoolingOff((current) => current.map((answer, i) => i === index ? value : answer))} className={`min-h-11 flex-1 rounded-lg border text-sm font-bold ${coolingOff[index] === value ? 'border-[#183f2a] bg-[#183f2a] text-white' : 'border-[#cbd5cb] text-[#526158]'}`} aria-pressed={coolingOff[index] === value}>{value ? t.yes : t.no}</button>)}</div></div>)}</fieldset>{hasStopSignal ? <div className="mt-6 rounded-2xl border border-[#e4aaa4] bg-[#fff0ee] p-5" role="alert"><h2 className="flex items-center gap-2 text-xl font-bold text-[#a52c24]"><AlertTriangle />{t.stop}</h2><p className="mt-2 text-sm leading-6 text-[#71332d]">{t.stopDetail}</p></div> : <p className="mt-6 text-center text-sm font-semibold text-[#637267]">{t.safe}</p>}<button onClick={() => setScreen('check')} className="mt-auto flex min-h-14 items-center justify-center gap-2 rounded-xl bg-[#183f2a] px-5 font-bold text-white">{t.back}</button></section>}
      <footer className="mt-10 flex items-center justify-center gap-2 text-xs text-[#89968c]"><Headphones /> Built for a calmer pause</footer>
    </div>
  </main>
}

export default SachetApp

export type { Analysis }
