from typing import Literal

from pydantic import BaseModel, Field

Lang = Literal["en", "hi", "hinglish"]
Verdict = Literal["likely_scam", "uncertain", "no_red_flags_found"]
Confidence = Literal["low", "medium", "high"]
AnalysisMode = Literal["rules+llm", "rules_only"]
LlmStage = Literal["request", "http", "parse", "validate", "timeout", "ok"]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    lang: Lang = "en"


class RedFlag(BaseModel):
    id: str
    label_en: str
    label_hi: str
    evidence: str


class SebiRegistration(BaseModel):
    claimed: str | None
    format_valid: bool | None
    check_link: str


class LlmDebug(BaseModel):
    """Temporary debug field — remove before final submission. Never contains keys or user text."""

    stage: LlmStage
    http_status: int | None = None
    error_type: str | None = None
    raw_preview: str | None = None


class AnalyzeResponse(BaseModel):
    verdict: Verdict
    risk_score: int = Field(..., ge=0, le=100)
    confidence: Confidence
    red_flags: list[RedFlag]
    explanation_en: str
    explanation_hi: str
    next_steps_en: list[str]
    next_steps_hi: list[str]
    sebi_registration: SebiRegistration
    disclaimer: str
    pii_redacted: Literal[True] = True
    analysis_mode: AnalysisMode
    llm_debug: LlmDebug


class LlmClassification(BaseModel):
    verdict: Verdict
    risk_score: int = Field(..., ge=0, le=100)
    confidence: Confidence
    scam_type: str | None = None
    flags: list[RedFlag] = Field(default_factory=list)
    explanation_en: str
    explanation_hi: str
