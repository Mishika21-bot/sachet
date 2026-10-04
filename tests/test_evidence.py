from app.redact import redact
from app.rules import clip_evidence, detect_red_flags, finish_placeholders


def test_clip_evidence_extends_split_upi_placeholder() -> None:
    prefix = "n" * 196
    source = prefix + "[UPI] immediately"
    snippet = clip_evidence(source, 0, 10, limit=200)
    assert "[UPI]" in snippet
    assert snippet.count("[") == snippet.count("]")
    assert not snippet.endswith("[UPI")
    assert not snippet.endswith("[UP")
    assert not snippet.endswith("[U")


def test_finish_placeholders_repairs_truncated_token() -> None:
    source = "Pay Rs 5000 to [UPI] now, limited seats"
    repaired = finish_placeholders("Pay Rs 5000 to [UPI", source)
    assert "[UPI]" in repaired
    assert not repaired.endswith("[UPI")
    standalone = finish_placeholders("Pay Rs 5000 to [U")
    assert standalone.endswith("[UPI]")


def test_redacted_payment_evidence_contains_full_upi() -> None:
    redacted = redact("Pay Rs 5000 to 98xxxxxx@upi now, limited seats!")
    assert "[UPI]" in redacted
    flags = detect_red_flags(redacted)
    payment = next(flag for flag in flags if flag.id == "personal_payment")
    assert "[UPI]" in payment.evidence or "upi" in payment.evidence.lower()
    if "[" in payment.evidence:
        assert payment.evidence.count("[") == payment.evidence.count("]")
