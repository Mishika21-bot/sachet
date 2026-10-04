"""Single LLM entry point. Defaults to Google Gemini; never hard-code keys."""

from __future__ import annotations

import time
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError

from app.models import LlmClassification, LlmDebug, RedFlag

logger = logging.getLogger("sachet.llm")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DOTENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(_DOTENV_PATH, override=True)

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.8-flash"
_RETIRED_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gpt-4o-mini",
}

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "verdict": {
            "type": "STRING",
            "enum": ["likely_scam", "uncertain", "no_red_flags_found"],
        },
        "risk_score": {"type": "INTEGER"},
        "confidence": {"type": "STRING", "enum": ["low", "medium", "high"]},
        "scam_type": {"type": "STRING", "nullable": True},
        "flags": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING"},
                    "label_en": {"type": "STRING"},
                    "label_hi": {"type": "STRING"},
                    "evidence": {"type": "STRING"},
                },
                "required": ["id", "label_en", "label_hi", "evidence"],
            },
        },
        "explanation_en": {"type": "STRING"},
        "explanation_hi": {"type": "STRING"},
    },
    "required": [
        "verdict",
        "risk_score",
        "confidence",
        "flags",
        "explanation_en",
        "explanation_hi",
    ],
}

SYSTEM_PROMPT = """You are Sachet, a public-good investor-protection assistant for India.
You ONLY help people spot likely investment scams in messages.

Hard rules:
- Do NOT say whether any stock, IPO, mutual fund, crypto, or other security is good or bad.
- Do NOT give buy, sell, or hold advice, price targets, or return forecasts.
- Do NOT promote or recommend any broker, app, tip service, or product.
- Do NOT claim a SEBI registration number is verified; format checks happen elsewhere.
- Work from the already-redacted text only. Do not ask for the original PII.
- Write explanations in simple language (around Class 8 reading level).
- explanation_hi must be natural Hindi in Devanagari.
- For every flag, "evidence" must be an exact phrase copied word-for-word from the message. Never paraphrase or describe it.
- A message that only gives routine account information (statements, SIP or dividend credits, maintenance charges), warns people about scams, or asks whether something is a scam is NOT a scam by itself. Mark it no_red_flags_found unless it also asks for money, an OTP or PIN, a link click, an app install, personal details, or joining a group.

Return JSON only, matching the provided response schema. No markdown fences.
"""


class LlmError(Exception):
    """Raised when the LLM is unavailable, times out, or returns unusable output."""

    def __init__(self, message: str, debug: LlmDebug | None = None) -> None:
        super().__init__(message)
        self.debug = debug or LlmDebug(stage="request", error_type=type(self).__name__)


def _redact_secrets(text: str) -> str:
    text = re.sub(r"([?&]key=)[^&\s]+", r"\1[REDACTED]", text, flags=re.I)
    text = re.sub(r"(AIza[0-9A-Za-z_\-]{10,}|AQ\.[0-9A-Za-z_\-]{10,})", "[REDACTED]", text)
    return text


def raw_preview(text: str, limit: int = 120) -> str:
    return _redact_secrets(text)[:limit]


def key_status() -> dict[str, Any]:
    """Safe diagnostics: never include the key value."""
    source = None
    length = 0
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "LLM_API_KEY"):
        value = os.getenv(name, "").strip()
        if value:
            source = name
            length = len(value)
            break
    env_model = os.getenv("LLM_MODEL", "").strip()
    return {
        "dotenv_path": str(_DOTENV_PATH),
        "dotenv_exists": _DOTENV_PATH.is_file(),
        "key_found": "yes" if source else "no",
        "key_var": source,
        "key_length": length,
        "env_model": env_model or None,
        "default_model": DEFAULT_MODEL,
        "model": env_model or DEFAULT_MODEL,
    }


def resolved_model_name() -> str:
    env_model = os.getenv("LLM_MODEL", "").strip()
    model = env_model or DEFAULT_MODEL
    if model.lower() in _RETIRED_MODELS:
        return DEFAULT_MODEL
    return model


def log_key_status() -> None:
    info = key_status()
    resolved = resolved_model_name() if info["key_found"] == "yes" else info["default_model"]
    logger.info(
        "llm env dotenv=%s exists=%s key found: %s var=%s length=%s "
        "LLM_MODEL_env=%s overrides=%s resolved_model=%s",
        info["dotenv_path"],
        info["dotenv_exists"],
        info["key_found"],
        info["key_var"],
        info["key_length"],
        info["env_model"] or "(unset)",
        bool(info["env_model"]),
        resolved,
    )


def _api_key() -> str:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "LLM_API_KEY"):
        value = os.getenv(name, "").strip()
        if value:
            return value
    raise LlmError(
        "GEMINI_API_KEY (or GOOGLE_API_KEY / LLM_API_KEY) is not set",
        LlmDebug(stage="request", error_type="MissingApiKey"),
    )


def _client_config() -> tuple[str, str, str, float]:
    api_key = _api_key()
    base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = resolved_model_name()
    timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
    return api_key, base_url, model, timeout


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fenced:
        return fenced.group(1).strip()
    return text


def _extract_json(raw: str) -> dict[str, Any]:
    return json.loads(_strip_fences(raw))


def _gemini_text(body: dict[str, Any]) -> tuple[str, str | None]:
    candidates = body.get("candidates") or []
    if not candidates:
        return "", None
    cand = candidates[0]
    parts = (cand.get("content") or {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    return text, cand.get("finishReason")


def _log_classify_failure(debug: LlmDebug) -> None:
    logger.warning(
        "classify failed type=%s status=%s stage=%s",
        debug.error_type,
        debug.http_status,
        debug.stage,
    )


def _generation_config() -> dict[str, Any]:
    return {
        "temperature": 0.1,
        "maxOutputTokens": 8192,
        "responseMimeType": "application/json",
        "responseSchema": RESPONSE_SCHEMA,
        "thinkingConfig": {"thinkingBudget": 0},
    }


def _model_chain() -> list[str]:
    """Primary model first, then backups. A bad/unknown backup is simply skipped."""
    chain = [resolved_model_name()]
    extra = os.getenv("LLM_FALLBACK_MODELS", "gemini-flash-latest,gemini-flash-lite-latest")
    for name in (m.strip() for m in extra.split(",")):
        if name and name not in chain and name.lower() not in _RETIRED_MODELS:
            chain.append(name)
    return chain


def _build_payload(redacted_text: str, lang: str, with_thinking: bool) -> dict[str, Any]:
    cfg = _generation_config()
    if not with_thinking:
        cfg.pop("thinkingConfig", None)
    return {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Message language hint: {lang}\n\n"
                            f"Redacted message:\n{redacted_text}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": cfg,
    }


def _call_model(
    client: httpx.Client,
    base_url: str,
    model: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float,
) -> tuple[LlmClassification, LlmDebug]:
    url = f"{base_url}/models/{model}:generateContent"
    try:
        response = client.post(
            url,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            json=payload,
            timeout=timeout,
        )
    except httpx.TimeoutException as exc:
        debug = LlmDebug(stage="timeout", error_type=type(exc).__name__)
        raise LlmError("LLM timed out", debug) from exc
    except Exception as exc:
        debug = LlmDebug(stage="request", error_type=type(exc).__name__)
        raise LlmError("LLM request failed", debug) from exc

    if response.status_code >= 400:
        debug = LlmDebug(
            stage="http", http_status=response.status_code, error_type="HTTPStatusError"
        )
        raise LlmError(f"LLM HTTP {response.status_code}", debug)

    try:
        content, finish = _gemini_text(response.json())
    except Exception as exc:
        debug = LlmDebug(
            stage="parse", http_status=response.status_code, error_type=type(exc).__name__
        )
        raise LlmError("LLM envelope parse failed", debug) from exc

    if not content.strip():
        debug = LlmDebug(
            stage="parse",
            http_status=response.status_code,
            error_type=finish or "EmptyModelReply",
            raw_preview=raw_preview(f"(empty finishReason={finish})"),
        )
        raise LlmError("LLM returned empty text", debug)

    try:
        data = _extract_json(content)
    except Exception as exc:
        debug = LlmDebug(
            stage="parse",
            http_status=response.status_code,
            error_type=type(exc).__name__,
            raw_preview=raw_preview(content),
        )
        raise LlmError("LLM returned invalid JSON", debug) from exc

    try:
        flags = [RedFlag.model_validate(item) for item in data.get("flags") or []]
        classification = LlmClassification(
            verdict=data["verdict"],
            risk_score=int(data["risk_score"]),
            confidence=data["confidence"],
            scam_type=data.get("scam_type"),
            flags=flags,
            explanation_en=data["explanation_en"],
            explanation_hi=data["explanation_hi"],
        )
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        debug = LlmDebug(
            stage="validate", http_status=response.status_code, error_type=type(exc).__name__
        )
        raise LlmError("LLM JSON failed validation", debug) from exc

    return classification, LlmDebug(stage="ok", http_status=response.status_code, error_type=None)


def classify(redacted_text: str, lang: str) -> tuple[LlmClassification, LlmDebug]:
    """Classify redacted text. Retries, backup models, and a hard total time budget."""
    try:
        api_key, base_url, _model, _timeout = _client_config()
    except LlmError:
        raise
    except Exception as exc:
        debug = LlmDebug(stage="request", error_type=type(exc).__name__)
        _log_classify_failure(debug)
        raise LlmError("LLM request setup failed", debug) from exc

    budget = float(os.getenv("LLM_TOTAL_BUDGET_SECONDS", "25"))
    per_try = float(os.getenv("LLM_ATTEMPT_TIMEOUT_SECONDS", "12"))
    deadline = time.monotonic() + budget
    last: LlmError | None = None

    with httpx.Client() as client:
        for model in _model_chain():
            with_thinking = True
            for _ in range(2):
                remaining = deadline - time.monotonic()
                if remaining < 2:
                    break
                payload = _build_payload(redacted_text, lang, with_thinking)
                started = time.monotonic()
                try:
                    return _call_model(
                        client, base_url, model, api_key, payload, min(per_try, remaining)
                    )
                except LlmError as exc:
                    last = exc
                    d = exc.debug
                    logger.warning(
                        "llm attempt failed model=%s secs=%.1f stage=%s status=%s type=%s",
                        model, time.monotonic() - started, d.stage, d.http_status, d.error_type,
                    )
                    if d.http_status == 400 and with_thinking:
                        with_thinking = False  # retry once without thinkingConfig
                        continue
                    if d.http_status == 429:
                        break  # quota hit on this model: don't hammer it, try the next model
                    retryable = d.stage in ("timeout", "parse", "validate") or d.http_status in (
                        500, 502, 503, 504,
                    )
                    if not retryable:
                        break  # e.g. 404 model not found -> next model
                    time.sleep(min(1.0, max(0.0, deadline - time.monotonic() - 2)))
            if deadline - time.monotonic() < 2:
                break

    final = last or LlmError(
        "LLM unavailable", LlmDebug(stage="request", error_type="NoAttempt")
    )
    _log_classify_failure(final.debug)
    raise final