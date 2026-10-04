# Sachet

Public-good **scam-pattern checker** for Indian retail investors (SANGYAN hackathon — investor protection). It is **not** a fintech product, **not** investment advice, and **not** a SEBI registration verification service.

Message text is redacted in memory (phones, UPI IDs, emails, bank/Aadhaar-like numbers) **before** any LLM call. Content is never logged or stored.

## Setup

Python 3.11+ recommended.

```powershell
cd C:\Users\DELL\Desktop\Sachet
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Optional: put a Google AI Studio Gemini key in `.env` as `GEMINI_API_KEY` (or `GOOGLE_API_KEY` / `LLM_API_KEY`). Default model is `gemini-2.5-flash`. If the key is missing or the model times out, Sachet still runs using **rules-only** detection.

## Run tests

```powershell
pytest -q
```

## Run the API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the interactive docs at:

**http://127.0.0.1:8000/docs**

(Alternative schema UI: http://127.0.0.1:8000/redoc)

`POST /analyze` body:

```json
{ "text": "string", "lang": "en" }
```

`lang` must be `en`, `hi`, or `hinglish`.

`analysis_mode` is `rules+llm` when Gemini/classify ran, or `rules_only` on fallback.

## Design

| Module | Role |
| --- | --- |
| `app/redact.py` | Strip PII before LLM |
| `app/rules.py` | Offline red flags (English / Hindi / Hinglish) |
| `app/llm.py` | **Single** LLM function (`classify`) |
| `app/decide.py` | Merge rules + LLM; disagreement → `uncertain`; LLM failure → rules-only |
| `app/guardrail.py` | Block buy/sell/hold, price calls, broker promotion |
| `app/sebi.py` | Format-only INH/INA/INZ + 9 digits; official search link, **not** verified |

`next_steps_en` and `next_steps_hi` list the same reporting steps in matching order: cybercrime 1930 / https://cybercrime.gov.in, SEBI SCORES, and SEBI's intermediary search link.
