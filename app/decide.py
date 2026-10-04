"""Combine rules + LLM. LLM failure -> rules-only fallback (clearly labelled)."""

from __future__ import annotations

import logging
import re

from app.guardrail import apply_guardrails
from app.llm import LlmError, classify
from app.models import AnalyzeResponse, LlmClassification, LlmDebug, RedFlag
from app.redact import redact
from app.rules import detect_red_flags, finish_placeholders, risk_score_from_flags, rules_verdict
from app.sebi import SEBI_INTERMEDIARY_SEARCH, extract_sebi_registration

logger = logging.getLogger("sachet.decide")

DISCLAIMER = (
    "Sachet is a public-good scam-pattern checker for investor protection. "
    "It is not a SEBI product, not financial advice, and not a verification of "
    "any intermediary. A matching registration-number format does not mean the "
    "person is registered. Always confirm on SEBI's official website."
)

_NEUTRAL_EN = (
    "Our checks did not find specific scam warning signs in this message. That does not "
    "prove it is safe. If money, a link, an app or personal details were requested, stop "
    "and verify through the official app or website."
)
_NEUTRAL_HI = (
    "हमारी जाँच में इस संदेश में ठगी का कोई स्पष्ट संकेत नहीं मिला। इसका मतलब यह नहीं कि संदेश "
    "सुरक्षित है। अगर पैसे, लिंक, ऐप या निजी जानकारी माँगी गई हो तो रुकें और आधिकारिक ऐप या "
    "वेबसाइट से जाँच करें।"
)
_CAUTION_EN = (
    "Sachet could not point to a specific warning sign in this message, but it is not fully "
    "sure. Do not pay, click, install or share anything until you verify through the official "
    "app or website."
)
_CAUTION_HI = (
    "सचेत को इस संदेश में कोई स्पष्ट संकेत नहीं मिला, लेकिन पूरी तरह भरोसा भी नहीं है। आधिकारिक ऐप "
    "या वेबसाइट से जाँचे बिना पैसे न दें, लिंक न खोलें, ऐप इंस्टॉल न करें और जानकारी साझा न करें।"
)


def _next_steps(verdict: str, check_link: str) -> tuple[list[str], list[str]]:
    link = check_link or SEBI_INTERMEDIARY_SEARCH
    steps_en = [
        "Do not pay anyone, share OTP/PIN, or install APK / remote-access apps from this chat.",
        "Report financial cyber fraud: call 1930 (24x7) and file at https://cybercrime.gov.in",
        "Complain against a SEBI-registered entity or listed company: https://scores.sebi.gov.in ; SEBI toll-free 1800 22 7575 / 1800 266 7575",
        f"Check whether an adviser/broker is registered using SEBI's official intermediary search: {link}",
    ]
    steps_hi = [
        "किसी को पैसे न दें, OTP/PIN न बताएँ, और इस चैट से APK / रिमोट-एक्सेस ऐप इंस्टॉल न करें।",
        "वित्तीय साइबर धोखाधड़ी की रिपोर्ट करें: 1930 पर कॉल करें (24x7) और https://cybercrime.gov.in पर शिकायत दर्ज करें",
        "SEBI-पंजीकृत संस्था या सूचीबद्ध कंपनी के विरुद्ध शिकायत: https://scores.sebi.gov.in ; SEBI टोल-फ्री 1800 22 7575 / 1800 266 7575",
        f"सलाहकार/ब्रोकर पंजीकृत है या नहीं, SEBI की आधिकारिक मध्यस्थ खोज पर जाँचें: {link}",
    ]
    if verdict == "no_red_flags_found":
        steps_en.insert(
            0,
            "No common red-flag phrases were found; still verify any investment offer independently.",
        )
        steps_hi.insert(
            0,
            "आम रेड-फ्लैग वाक्य नहीं मिले; फिर भी किसी भी निवेश प्रस्ताव की स्वतंत्र जाँच करें।",
        )
    return steps_en, steps_hi


def _merge_flags(
    rule_flags: list[RedFlag],
    llm_flags: list[RedFlag],
    redacted_source: str,
) -> list[RedFlag]:
    merged: list[RedFlag] = []
    seen: set[str] = set()
    for flag in [*rule_flags, *llm_flags]:
        if flag.id in seen:
            continue
        seen.add(flag.id)
        merged.append(
            flag.model_copy(
                update={"evidence": finish_placeholders(flag.evidence, redacted_source)}
            )
        )
    return merged


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _grounded_flags(flags: list[RedFlag], redacted: str) -> list[RedFlag]:
    """Keep only AI flags whose evidence is a real phrase from the message:
    not a paraphrase, and not the entire message."""
    source = _norm(redacted)
    edge = " .\"'“”‘’"
    kept: list[RedFlag] = []
    for flag in flags:
        evidence = _norm(flag.evidence)
        fragments = [p.strip(edge) for p in re.split(r"\.{3}|…", evidence)]
        fragments = [p for p in fragments if p]
        if not fragments or any(len(p) < 4 or p not in source for p in fragments):
            continue
        if len(source) > 60 and len(" ".join(fragments)) >= 0.9 * len(source):
            continue
        kept.append(flag)
    return kept


def _rules_explanations(flags: list[RedFlag]) -> tuple[str, str]:
    if not flags:
        return (
            "Limited check: the AI service was unavailable, and our offline rules found "
            "no known scam phrases. This is NOT a safety guarantee. If money, apps or "
            "remote access were requested, stop and verify the person independently.",
            "सीमित जाँच: AI सेवा उपलब्ध नहीं थी और हमारे ऑफ़लाइन नियमों को कोई जाना-पहचाना "
            "ठगी वाला वाक्य नहीं मिला। यह सुरक्षा की गारंटी नहीं है। अगर पैसे, ऐप या रिमोट "
            "एक्सेस माँगा गया हो तो रुकें और व्यक्ति की स्वतंत्र जाँच करें।",
        )
    labels = ", ".join(f.label_en for f in flags)
    labels_hi = ", ".join(f.label_hi for f in flags)
    return (
        "This message matches known investment-scam patterns: "
        f"{labels}. Do not pay, share OTP, or install apps from this sender. "
        "This is a pattern check, not a judgement on any stock.",
        "यह संदेश निवेश-ठगी के ज्ञात पैटर्न से मेल खाता है: "
        f"{labels_hi}। इस भेजने वाले को पैसे न दें, OTP न बताएँ, ऐप इंस्टॉल न करें। "
        "यह पैटर्न जाँच है, किसी शेयर पर राय नहीं।",
    )


def _fallback_verdict(rv: str, flags: list[RedFlag]) -> tuple[str, int]:
    """AI unavailable: never show a green all-clear; keep verdict and score consistent."""
    score = risk_score_from_flags(flags)
    if not flags:
        return "uncertain", 35
    if rv == "likely_scam":
        return "likely_scam", max(score, 70)
    return "uncertain", min(max(score, 40), 69)


def analyze(text: str, lang: str) -> AnalyzeResponse:
    redacted = redact(text)
    rule_flags = detect_red_flags(redacted)
    rv = rules_verdict(rule_flags)
    sebi = extract_sebi_registration(redacted)

    llm_result: LlmClassification | None = None
    llm_debug = LlmDebug(stage="request", error_type="NotAttempted")
    try:
        classified = classify(redacted, lang)
        if isinstance(classified, tuple):
            llm_result, llm_debug = classified
        else:
            llm_result = classified
            llm_debug = LlmDebug(stage="ok", error_type=None)
    except LlmError as exc:
        llm_debug = exc.debug or LlmDebug(stage="request", error_type=type(exc).__name__)
        logger.warning(
            "classify failed type=%s status=%s",
            llm_debug.error_type,
            llm_debug.http_status,
        )
        llm_result = None

    if llm_result is None:
        explanation_en, explanation_hi = _rules_explanations(rule_flags)
        rule_flags = [
            f.model_copy(update={"evidence": finish_placeholders(f.evidence, redacted)})
            for f in rule_flags
        ]
        fb_verdict, fb_risk = _fallback_verdict(rv, rule_flags)
        steps_en, steps_hi = _next_steps(fb_verdict, sebi.check_link)
        response = AnalyzeResponse(
            verdict=fb_verdict,  # type: ignore[arg-type]
            risk_score=fb_risk,
            confidence="medium" if rule_flags else "low",
            red_flags=rule_flags,
            explanation_en=explanation_en,
            explanation_hi=explanation_hi,
            next_steps_en=steps_en,
            next_steps_hi=steps_hi,
            sebi_registration=sebi,
            disclaimer=DISCLAIMER,
            pii_redacted=True,
            analysis_mode="rules_only",
            llm_debug=llm_debug,
        )
        return apply_guardrails(response)

    rules_score = risk_score_from_flags(rule_flags)
    grounded = _grounded_flags(llm_result.flags, redacted)
    lv = llm_result.verdict
    downgraded = False
    if not rule_flags and not grounded:
        # The AI cannot point to anything concrete in the message: be more cautious, not more alarming.
        if lv == "likely_scam":
            lv, downgraded = "uncertain", True
        elif lv == "uncertain":
            lv, downgraded = "no_red_flags_found", True
    llm_has_evidence = bool(grounded)
    llm_sure = llm_result.confidence in ("medium", "high")

    if lv == rv:
        verdict = lv
        confidence = llm_result.confidence
    elif not rule_flags:
        # Rules are silent (they only know listed phrases). Silence is not proof of safety.
        if lv == "likely_scam" and llm_has_evidence and llm_sure:
            verdict, confidence = "likely_scam", "medium"
        elif lv == "no_red_flags_found":
            verdict, confidence = "no_red_flags_found", llm_result.confidence
        else:
            verdict, confidence = "uncertain", "low"
    elif lv == "no_red_flags_found":
        # Rules found patterns but the model sees none: honest disagreement.
        verdict, confidence = "uncertain", "low"
    else:
        # One side says likely_scam, the other says uncertain.
        verdict = "likely_scam" if "likely_scam" in (rv, lv) else "uncertain"
        confidence = "medium" if verdict == "likely_scam" else "low"
    if downgraded:
        confidence = "low"

    blended = int((llm_result.risk_score + rules_score) / 2)
    if verdict == lv == rv:
        risk = max(rules_score, blended)
    else:
        risk = max(llm_result.risk_score, rules_score)
    if verdict == "uncertain":
        risk = min(risk, 69)
    elif verdict == "likely_scam":
        risk = max(risk, 70)
    else:
        risk = min(risk, 30)
    risk = min(100, max(0, risk))

    if downgraded and verdict == "no_red_flags_found":
        explanation_en, explanation_hi = _NEUTRAL_EN, _NEUTRAL_HI
    elif downgraded:
        explanation_en, explanation_hi = _CAUTION_EN, _CAUTION_HI
    else:
        explanation_en, explanation_hi = llm_result.explanation_en, llm_result.explanation_hi

    flags = _merge_flags(rule_flags, grounded, redacted)
    steps_en, steps_hi = _next_steps(verdict, sebi.check_link)
    response = AnalyzeResponse(
        verdict=verdict,
        risk_score=risk,
        confidence=confidence,
        red_flags=flags,
        explanation_en=explanation_en,
        explanation_hi=explanation_hi,
        next_steps_en=steps_en,
        next_steps_hi=steps_hi,
        sebi_registration=sebi,
        disclaimer=DISCLAIMER,
        pii_redacted=True,
        analysis_mode="rules+llm",
        llm_debug=llm_debug,
    )
    return apply_guardrails(response)