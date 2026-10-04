from app.llm import _strip_fences, raw_preview


def test_strip_fences_before_parse() -> None:
    raw = '```json\n{"verdict": "uncertain"}\n```'
    assert _strip_fences(raw) == '{"verdict": "uncertain"}'


def test_raw_preview_is_capped_and_redacts_keys() -> None:
    blob = "x" * 200 + " key=AIzaSyDummyKeyValueForTestOnlyXX"
    preview = raw_preview(blob)
    assert len(preview) <= 120
    assert "AIza" not in preview
