"""HTTP API. Request bodies are never logged."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.decide import analyze
from app.llm import log_key_status
from app.models import AnalyzeRequest, AnalyzeResponse

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("sachet")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log_key_status()
    yield


app = FastAPI(
    title="Sachet",
    version="0.1.0",
    description=(
        "Investor-protection scam-pattern checker for Indian retail investors "
        "(SANGYAN hackathon). Public good — not a fintech product, not advice."
    ),
    lifespan=lifespan,
)


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*" or not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()] or ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sachet"}


@app.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    logger.info("analyze requested lang=%s chars=%s", body.lang, len(body.text))
    return analyze(body.text, body.lang)

@app.get("/")
def root():
    return {"service": "sachet", "docs": "/docs", "health": "/health"}