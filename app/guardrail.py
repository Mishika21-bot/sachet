"""Scan every outbound field; strip buy/sell/hold advice, price calls, and product promotion."""

from __future__ import annotations

import re
from typing import Any

from app.models import AnalyzeResponse, RedFlag

_ADVICE = re.compile(
    r"\b("
    r"buy\s+this\s+stock|sell\s+this\s+stock|hold\s+this\s+stock|"
    r"you\s+should\s+(buy|sell|hold)|recommend(ed)?\s+(buying|selling)|"
    r"strong\s+(buy|sell)|price\s+target|target\s+price|"
    r"will\s+(go\s+to|reach|hit)\s+(rs\.?|₹)?\s*\d|"
    r"stock\s+will\s+(rise|fall|rally)|invest\s+in\s+this\s+(stock|scrip)|"
    r"open\s+(a\s+)?demat\s+with|use\s+(this\s+)?broker|"
    r"best\s+broker|sign\s+up\s+with\s+(zerodha|groww|upstox|angel)"
    r")\b",
    re.I,
)

_ADVICE_HI = re.compile(
    r"यह\s*शेयर\s*(खरीदें|बेचें|होल्ड)|शेयर\s*(खरीदो|बेचो)|"
    r"प्राइस\s*टारगेट|दाम\s*पहुंचेगा|"
    r"इस\s*ब्रोकर\s*(से|को)|बेस्ट\s*ब्रोकर"
)

SAFE_EXPLANATION_EN = (
    "This tool only flags common scam patterns. It does not say whether any "
    "security is good or bad, and it does not recommend any broker or product."
)
SAFE_EXPLANATION_HI = (
    "यह टूल केवल आम ठगी के पैटर्न दर्शाता है। यह किसी भी शेयर को अच्छा या बुरा "
    "नहीं बताता और किसी ब्रोकर या उत्पाद की सिफारिश नहीं करता।"
)


def contains_prohibited_advice(text: str) -> bool:
    if not text:
        return False
    return bool(_ADVICE.search(text) or _ADVICE_HI.search(text))


def _clean_text(value: str) -> str:
    if contains_prohibited_advice(value):
        return SAFE_EXPLANATION_EN
    return value


def apply_guardrails(response: AnalyzeResponse) -> AnalyzeResponse:
    data: dict[str, Any] = response.model_dump()
    if contains_prohibited_advice(data["explanation_en"]):
        data["explanation_en"] = SAFE_EXPLANATION_EN
    if contains_prohibited_advice(data["explanation_hi"]):
        data["explanation_hi"] = SAFE_EXPLANATION_HI

    cleaned_en: list[str] = []
    cleaned_hi: list[str] = []
    for step_en, step_hi in zip(data["next_steps_en"], data["next_steps_hi"], strict=True):
        if contains_prohibited_advice(step_en) or contains_prohibited_advice(step_hi):
            continue
        cleaned_en.append(step_en)
        cleaned_hi.append(step_hi)
    data["next_steps_en"] = cleaned_en
    data["next_steps_hi"] = cleaned_hi

    cleaned_flags: list[RedFlag] = []
    for flag in data["red_flags"]:
        evidence = flag["evidence"]
        if contains_prohibited_advice(evidence):
            evidence = "[redacted: investment advice removed]"
        cleaned_flags.append(
            RedFlag(
                id=flag["id"],
                label_en=flag["label_en"],
                label_hi=flag["label_hi"],
                evidence=evidence,
            )
        )
    data["red_flags"] = cleaned_flags
    return AnalyzeResponse.model_validate(data)
