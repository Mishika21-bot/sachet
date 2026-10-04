# 🛡️ Sachet (सचेत) — Project Core Infrastructure

A zero-cost, localized public-good investor-protection infrastructure designed for emerging retail investors in Tier-2 and Tier-3 Indian cities. It translates chaotic, predatory scam vectors into clear safety signals and actionable legal remediation.

This is a public-good framework: it does not promote investment, does not provide advice, and does not sell fintech products.

## 🚀 Unified Architectural Ecosystem

- `/frontend`: Optimized React/Next.js interface featuring regional multi-lingual toggles, native voice dictation `SpeechRecognition`), client-side speech playback, and an automatic network outage edge fallback state layer.
- `/app`: High-performance FastAPI analytical engine driving our privacy-first data pipelines and keyword guardrail suppression architectures.

## 🔒 Multi-Layer Hybrid Detection Pipeline

1. **PII Masking `app/redact.py`)**: Sanitizes sensitive user data identifiers (UPI IDs, phone numbers, bank accounts) in-memory before external processing.
2. **Deterministic Core `app/rules.py`)**: Evaluates payload metadata across 20 unique local regex pattern families for 0ms latency screening.
3. **AI Core Layer `app/decide.py` / `app/llm.py`)**: Sources highly structured analytical second opinions from the Gemini API using PII-blinded payload strings.
4. **SEBI Compliance Guardrail `app/guardrail.py`)**: Enforces an absolute output filter that drops stock recommendations or broker promotions instantly.
5. **Unified Channel Ingress `app/webhook.py`)**: Native API webhook endpoint configured to ingest direct message container flows from Telegram bot polling frameworks or WhatsApp Business API integrations.

## 🛠️ Local Environment Workspace Setup

### 1. Engine Initialization

```bash


python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
copy .env.example .env

```

*Note: Populate the* `GEMINI_API_KEY` *inside your environment* `.env` *file. If the cloud key is missing or encounters a network timeout, Sachet gracefully switches to a secure* `rules_only` *fallback assessment state.*

### 2. Run Automated Integration Suites

Validate pipeline components and mock data behaviors via pytest:

```bash

pytest tests/test_[webhook.py](http://webhook.py) -v

```

### 3. Launch Local Hot-Reloading Development Gateway Server

```bash

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```

- Interactive Swagger Endpoint Panel: `http://127.0.0`
- Unified Chat Messaging Channel Webhook Route: `POST /v1/webhooks/message-channel`

---

*Built for the Sangyan Hackathon (IIT BHU x SEBI x NSDL) — Committed to securing India's retail investment space.*