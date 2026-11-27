
"""FastAPI entry point for the LedgerLock application."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import router
from app.ledger_core import AuditLedger


BASE_DIR = Path(__file__).resolve().parent

API_MODE = os.getenv("LEDGERLOCK_API_MODE", "mock").strip().lower()

if API_MODE not in {"mock", "live"}:
    raise RuntimeError(
        "LEDGERLOCK_API_MODE must be either 'mock' or 'live'."
    )


app = FastAPI(
    title="LedgerLock",
    description="Tamper-evident audit-ledger demonstration",
    version="0.1.0",
)

app.state.ledger = AuditLedger()
app.state.checkpoint = None

app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.exception_handler(RequestValidationError)
async def safe_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request

    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]),
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Request validation failed.",
            "errors": errors,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_mode": API_MODE},
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ledgerlock-frontend",
        "api_mode": API_MODE,
    }
