"""FastAPI entry point for the LedgerLock integration baseline.

The API uses a disposable in-memory ledger. Persistent storage, signed
checkpoints and cloud-service verification remain explicitly unavailable.
"""

from __future__ import annotations

import os
from pathlib import Path

from typing import Literal

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.ledger_core import AuditLedger


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


class EventCreate(BaseModel):
    """Validated synthetic event supplied by the demonstration client."""

    model_config = {"str_strip_whitespace": True, "extra": "forbid"}

    event_type: Literal[
        "access",
        "configuration",
        "verification",
        "authentication",
    ]
    actor_id: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=1, max_length=120)
    resource_id: str = Field(min_length=1, max_length=64)
    outcome: Literal["success", "denied", "controlled_error"]


app.state.ledger = AuditLedger()


@app.exception_handler(RequestValidationError)
async def safe_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return useful field errors without echoing submitted values."""

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
        content={"message": "Request validation failed.", "errors": errors},
    )


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
        "service": "ledgerlock-api",
        "environment": "development",
    }


@app.post("/api/events", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate) -> dict[str, object]:
    """Append one validated synthetic event to the in-memory chain."""

    return app.state.ledger.add_event(event.model_dump())


@app.get("/api/ledger")
async def list_ledger() -> dict[str, object]:
    """Return the current chain and an honest checkpoint status."""

    records = app.state.ledger.get_records()
    return {
        "records": records,
        "count": len(records),
        "latest_sequence": records[-1]["sequence"] if records else None,
        "checkpoint": {"status": "unavailable", "key_version": None},
    }


@app.post("/api/verify")
async def verify_ledger() -> dict[str, object]:
    """Verify sequence and hash links without claiming checkpoint support."""

    result = app.state.ledger.verify_records(app.state.ledger.get_records())
    result["checkpoint_valid"] = False
    if result["valid"]:
        result["message"] = (
            "Hash chain verified. Signed checkpoint verification is unavailable."
        )
    return result
