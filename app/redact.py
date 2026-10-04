"""In-memory PII redaction. Never log or persist message content."""

from __future__ import annotations

import re

# Emails first so UPI patterns do not swallow them.
_EMAIL = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")

# UPI VPA: local-part @ handle (paytm, ybl, okaxis, upi, etc.)
_UPI = re.compile(
    r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9]{1,64}\b",
    re.IGNORECASE,
)

_PHONE_PLUS91 = re.compile(r"\+91[\s\-]?[6-9]\d{9}\b")
_PHONE_IN = re.compile(r"(?<!\d)(?:0)?[6-9]\d{9}(?!\d)")

_IFSC = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")

# Aadhaar-like 4-4-4 grouping
_AADHAAR_GROUPED = re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")

# Bank-account-like leftover digit runs (after phones/Aadhaar)
_BANKISH = re.compile(r"(?<!\d)\d{9,18}(?!\d)")


def redact(text: str) -> str:
    """Return a copy with phones, UPI IDs, bank/Aadhaar-like numbers, and emails removed."""
    out = _EMAIL.sub("[EMAIL]", text)
    out = _UPI.sub("[UPI]", out)
    out = _PHONE_PLUS91.sub("[PHONE]", out)
    out = _PHONE_IN.sub("[PHONE]", out)
    out = _IFSC.sub("[IFSC]", out)
    out = _AADHAAR_GROUPED.sub("[ID_NUMBER]", out)
    out = _BANKISH.sub("[ID_NUMBER]", out)
    return out
