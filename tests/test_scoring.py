import pytest

from app.decide import analyze
from app.llm import LlmError
from app.redact import redact
from app.rules import detect_red_flags, risk_score_from_flags

VIP_SCAM = (
    "Join our VIP group! Guaranteed 40% returns in 15 days. "
    "Pay Rs 5000 to 98xxxxxx@upi now, limited seats!"
)


def test_guaranteed_and_personal_pay_weigh_heavily() -> None:
    flags = detect_red_flags("Guaranteed returns. Pay to my personal UPI.")
    ids = {flag.id for flag in flags}
    assert "guaranteed_returns" in ids
    assert "personal_payment" in ids
    assert risk_score_from_flags(flags) >= 84


def test_vip_scam_message_rules_score_is_85_plus() -> None:
    redacted = redact(VIP_SCAM)
    flags = detect_red_flags(redacted)
    ids = {flag.id for flag in flags}
    assert "guaranteed_returns" in ids
    assert "unsolicited_group_invite" in ids
    assert "personal_payment" in ids
    assert risk_score_from_flags(flags) >= 85


def test_analyze_vip_scam_scores_85_plus_on_rules_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.decide.classify", lambda *_a, **_k: (_ for _ in ()).throw(LlmError("off")))
    result = analyze(VIP_SCAM, "en")
    ids = {flag.id for flag in result.red_flags}
    assert result.verdict == "likely_scam"
    assert "guaranteed_returns" in ids
    assert "unsolicited_group_invite" in ids
    assert result.risk_score >= 85
    assert result.analysis_mode == "rules_only"


def test_private_circle_message_analyze_likely_scam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.decide.classify", lambda *_a, **_k: (_ for _ in ()).throw(LlmError("off")))
    result = analyze(
        "Our senior analyst's private circle has been multiplying members' capital "
        "every month with zero downside. DM me for the entry window.",
        "en",
    )
    assert result.verdict == "likely_scam"
    ids = {flag.id for flag in result.red_flags}
    assert "unsolicited_group_invite" in ids
    assert "capital_multiplier" in ids
    assert "zero_risk_no_loss" in ids
    assert "dm_for_entry" in ids
