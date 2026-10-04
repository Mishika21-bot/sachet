"""SEBI registration number format check only — never claim verification."""

from __future__ import annotations

import re

from app.models import SebiRegistration

# Intermediary-style prefixes commonly cited in retail scams.
_SEBI_REG = re.compile(r"\b(IN[HAZ])\s*-?\s*(\d{9})\b", re.IGNORECASE)

SEBI_INTERMEDIARY_SEARCH = (
    "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes"
)


def extract_sebi_registration(text: str) -> SebiRegistration:
    match = _SEBI_REG.search(text)
    if not match:
        return SebiRegistration(
            claimed=None,
            format_valid=None,
            check_link=SEBI_INTERMEDIARY_SEARCH,
        )
    claimed = f"{match.group(1).upper()}{match.group(2)}"
    return SebiRegistration(
        claimed=claimed,
        format_valid=True,
        check_link=SEBI_INTERMEDIARY_SEARCH,
    )
