from app.guardrail import SAFE_EXPLANATION_EN, apply_guardrails, contains_prohibited_advice
from app.models import AnalyzeResponse, LlmDebug, SebiRegistration


def test_guardrail_detects_buy_this_stock() -> None:
    assert contains_prohibited_advice("You should buy this stock tomorrow.")


def test_guardrail_replaces_buy_this_stock_in_response() -> None:
    raw = AnalyzeResponse(
        verdict="uncertain",
        risk_score=10,
        confidence="low",
        red_flags=[],
        explanation_en="Analysts say buy this stock for quick gains.",
        explanation_hi="सामान्य जाँच।",
        next_steps_en=["Maybe buy this stock after listing."],
        next_steps_hi=["शायद यह शेयर खरीदें।"],
        sebi_registration=SebiRegistration(
            claimed=None,
            format_valid=None,
            check_link="https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes",
        ),
        disclaimer="test",
        pii_redacted=True,
        analysis_mode="rules_only",
        llm_debug=LlmDebug(stage="ok"),
    )
    out = apply_guardrails(raw)
    assert "buy this stock" not in out.explanation_en.lower()
    assert out.explanation_en == SAFE_EXPLANATION_EN
    assert out.next_steps_en == []
    assert out.next_steps_hi == []
