import pytest

from app.decide import analyze
from app.llm import LlmError
from app.models import LlmClassification, LlmDebug


def test_llm_failure_falls_back_to_rules_only(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_text: str, _lang: str):
        raise LlmError(
            "simulated timeout",
            LlmDebug(stage="timeout", error_type="TimeoutException"),
        )

    monkeypatch.setattr("app.decide.classify", boom)

    result = analyze(
        "Guaranteed returns, pay to my personal UPI, join our WhatsApp group.",
        "en",
    )
    assert result.verdict == "likely_scam"
    assert result.pii_redacted is True
    ids = {flag.id for flag in result.red_flags}
    assert "guaranteed_returns" in ids
    assert "personal_payment" in ids
    assert "unsolicited_group_invite" in ids
    assert result.confidence in {"low", "medium", "high"}
    assert 0 <= result.risk_score <= 100
    assert result.analysis_mode == "rules_only"
    assert result.llm_debug.stage == "timeout"
    assert result.llm_debug.error_type == "TimeoutException"
    joined = " ".join(result.next_steps_en + result.next_steps_hi)
    assert len(result.next_steps_en) == len(result.next_steps_hi)
    assert "TODO" not in joined
    assert "1930" in " ".join(result.next_steps_en)
    assert "1930" in " ".join(result.next_steps_hi)
    assert "https://cybercrime.gov.in" in joined
    assert "https://scores.sebi.gov.in" in joined
    assert "1800 22 7575" in joined
    assert "1800 266 7575" in joined
    assert result.sebi_registration.check_link in joined
    assert "वित्तीय साइबर धोखाधड़ी" in " ".join(result.next_steps_hi)
    assert "NSE" not in joined and "BSE" not in joined
    assert "helpline numbers before publishing" not in joined


def test_llm_failure_without_rules_is_uncertain_not_green(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_text: str, _lang: str):
        raise LlmError(
            "simulated timeout",
            LlmDebug(stage="timeout", error_type="TimeoutException"),
        )

    monkeypatch.setattr("app.decide.classify", boom)
    result = analyze("The market opened and closed as usual today.", "en")
    assert result.verdict == "uncertain"
    assert result.analysis_mode == "rules_only"
    assert result.risk_score < 70
    assert result.red_flags == []
    assert result.analysis_mode == "rules_only"
    assert result.llm_debug.stage == "timeout"


def test_analysis_mode_rules_plus_llm_when_classify_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_classify(_text: str, _lang: str):
        return (
            LlmClassification(
                verdict="no_red_flags_found",
                risk_score=8,
                confidence="medium",
                scam_type=None,
                flags=[],
                explanation_en="No usual scam phrases showed up.",
                explanation_hi="आम ठगी वाले वाक्य नहीं दिखे।",
            ),
            LlmDebug(stage="ok", http_status=200),
        )

    monkeypatch.setattr("app.decide.classify", fake_classify)
    result = analyze("The market opened and closed as usual today.", "en")
    assert result.analysis_mode == "rules+llm"
    assert result.verdict == "no_red_flags_found"
    assert result.llm_debug.stage == "ok"
