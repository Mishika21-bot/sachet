from app.redact import redact


def test_redact_removes_phone_upi_email_and_id_numbers():
    raw = (
        "Call +91 9876543210 or 09876543210. "
        "Pay ravi.kumar@oksbi and mail us at help@broker-tips.com. "
        "Aadhaar 2345 6789 0123 IFSC HDFC0001234 account 123456789012."
    )
    out = redact(raw)
    assert "+91" not in out
    assert "9876543210" not in out
    assert "09876543210" not in out
    assert "ravi.kumar@oksbi" not in out
    assert "help@broker-tips.com" not in out
    assert "2345 6789 0123" not in out
    assert "HDFC0001234" not in out
    assert "123456789012" not in out
    assert "[PHONE]" in out
    assert "[UPI]" in out
    assert "[EMAIL]" in out
    assert "[ID_NUMBER]" in out
    assert "[IFSC]" in out
