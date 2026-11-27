"""FastAPI entry point for the LedgerLock frontend foundation.

Ledger and cloud endpoints deliberately remain outside this module until their
owners implement the agreed API contract. Mock mode is a browser-only UI aid.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import router


BASE_DIR = Path(__file__).resolve().parent
API_MODE = os.getenv("LEDGERLOCK_API_MODE", "mock").strip().lower()
if API_MODE not in {"mock", "live"}:
    raise RuntimeError("LEDGERLOCK_API_MODE must be either 'mock' or 'live'.")

app = FastAPI(
    title="LedgerLock",
    description="Tamper-evident audit-ledger demonstration frontend",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the single-page dashboard with an explicit API-mode label."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_mode": API_MODE},
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Return a non-sensitive health response used by CI and deployments."""

    return {
        "status": "ok",
        "service": "ledgerlock-frontend",
        "api_mode": API_MODE,
    }
