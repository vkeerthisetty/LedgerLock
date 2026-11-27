
"""FastAPI entry point for the LedgerLock integration baseline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.ledger_core import AuditLedger
from app.security_logging import log_security_event


BASE_DIR = Path(__file__).resolve().parent

API_MODE = os.getenv(
    "LEDGERLOCK_API_MODE", "mock"
).strip().lower()

if API_MODE not in {"mock", "live"}:
    raise RuntimeError(
        "LEDGERLOCK_API_MODE must be either 'mock' or 'live'."
    )


app = FastAPI(
    title="LedgerLock",
    description="Tamper-evident audit-ledger demonstration frontend",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


# --------------------------------------------------
# Event validation
# --------------------------------------------------

class EventCreate(BaseModel):
    """Validated synthetic event supplied by the client."""

    model_config = {
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    event_type: Literal[
        "access",
        "configuration",
        "verification",
        "authentication",
    ]

    actor_id: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=1, max_length=120)
    resource_id: str = Field(min_length=1, max_length=64)

    outcome: Literal[
        "success",
        "denied",
        "controlled_error",
    ]


# --------------------------------------------------
# Ledger initialization
# --------------------------------------------------

app.state.ledger = AuditLedger()


# --------------------------------------------------
# Safe HTTP error handling
# --------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def safe_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Return controlled HTTP errors without internal details."""

    messages = {
        401: "Authentication is required.",
        403: "You are not authorised to perform this operation.",
        404: "The requested resource was not found.",
        405: "This operation is not allowed.",
        429: "Too many requests. Please try again later.",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": messages.get(
                    exc.status_code,
                    "The request could not be completed.",
                ),
            }
        },
    )


# --------------------------------------------------
# Safe validation error handling
# --------------------------------------------------

@app.exception_handler(RequestValidationError)
async def safe_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return safe validation information without submitted values."""

    errors = [
        {
            "field": ".".join(
                str(part) for part in error["loc"][1:]
            ),
            "type": error["type"],
        }
        for error in exc.errors()
    ]

    fields = list(
        dict.fromkeys(
            error["field"] for error in errors
        )
    )

    message = "Request validation failed."

    return JSONResponse(
        status_code=422,
        content={
            # Top-level fields for the API contract.
            "message": message,
            "errors": errors,

            # Nested fields for the security error contract.
            "error": {
                "code": "validation_error",
                "message": message,
                "fields": fields,
            },
        },
    )


# --------------------------------------------------
# Safe unexpected error handling
# --------------------------------------------------

@app.exception_handler(Exception)
async def safe_unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Hide internal exception details from API clients."""

    log_security_event(
        event_type="application_error",
        outcome="failure",
        error_category="unexpected_error",
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": (
                    "An unexpected error occurred. "
                    "Please try again later."
                ),
            }
        },
    )


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the dashboard with an explicit API-mode label."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_mode": API_MODE},
    )


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/api/health")
async def health() -> dict[str, str]:
    """Return a non-sensitive health response."""

    return {
        "status": "ok",
        "service": "ledgerlock-api",
        "environment": "development",
    }


# --------------------------------------------------
# Create event
# --------------------------------------------------

@app.post("/api/events", status_code=201)
async def create_event(
    event: EventCreate,
) -> dict[str, object]:
    """Append a validated synthetic event to the ledger."""

    return app.state.ledger.add_event(
        event.model_dump()
    )


# --------------------------------------------------
# Read ledger
# --------------------------------------------------

@app.get("/api/ledger")
async def list_ledger() -> dict[str, object]:
    """Return the current ledger and checkpoint status."""

    records = app.state.ledger.get_records()

    return {
        "records": records,
        "count": len(records),
        "latest_sequence": (
            records[-1]["sequence"] if records else None
        ),
        "checkpoint": {
            "status": "unavailable",
            "key_version": None,
        },
    }


# --------------------------------------------------
# Verify ledger
# --------------------------------------------------

@app.post("/api/verify")
async def verify_ledger() -> dict[str, object]:
    """Verify sequence and hash links."""

    result = app.state.ledger.verify_records(
        app.state.ledger.get_records()
    )

    result["checkpoint_valid"] = False

    if result["valid"]:
        result["message"] = (
            "Hash chain verified. "
            "Signed checkpoint verification is unavailable."
        )

    return result
