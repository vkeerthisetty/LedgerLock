"""FastAPI entry point for the LedgerLock integration baseline."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from signing.kms_adapter import CheckpointSignerAdapter

from app.api import router
from app.local_storage import LocalLedgerStorage
from app.security_logging import log_security_event
from storage.firestore_adapter import LedgerStorageAdapter


BASE_DIR = Path(__file__).resolve().parent
API_MODE = os.getenv("LEDGERLOCK_API_MODE", "mock").strip().lower()
APP_ENV = os.getenv("LEDGERLOCK_ENV", "development").strip().lower()
USE_CLOUD_SERVICES = (
    os.getenv("USE_CLOUD_SERVICES", "false").strip().lower() == "true"
)

if API_MODE not in {"mock", "live"}:
    raise RuntimeError(
        "LEDGERLOCK_API_MODE must be either 'mock' or 'live'."
    )

app = FastAPI(
    title="LedgerLock",
    description="Tamper-evident audit-ledger demonstration",
    version="0.1.0",
)

# Local mode preserves the existing in-memory ledger.
# Cloud mode uses the Firestore adapter.
if USE_CLOUD_SERVICES:
    app.state.storage = LedgerStorageAdapter(use_cloud=True)
    app.state.ledger = None
else:
    app.state.storage = LocalLedgerStorage()
    # Keep this alias for existing tests and compatibility.
    app.state.ledger = app.state.storage.ledger

app.state.checkpoint = app.state.storage.get_checkpoint()
app.state.signer = CheckpointSignerAdapter(
    use_cloud=USE_CLOUD_SERVICES
)
app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.exception_handler(StarletteHTTPException)
async def safe_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Return controlled HTTP errors without internal details."""

    del request
    messages = {
        401: "Authentication is required.",
        403: "You are not authorised to perform this operation.",
        404: "The requested resource was not found.",
        405: "This operation is not allowed.",
        409: "The operation conflicts with the current ledger state.",
        429: "Too many requests. Please try again later.",
        503: "The requested security service is not configured.",
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


@app.exception_handler(RequestValidationError)
async def safe_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return safe validation information without submitted values."""

    del request
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]),
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    fields = list(dict.fromkeys(error["field"] for error in errors))
    message = "Request validation failed."
    return JSONResponse(
        status_code=422,
        content={
            "message": message,
            "errors": errors,
            "error": {
                "code": "validation_error",
                "message": message,
                "fields": fields,
            },
        },
    )


@app.exception_handler(Exception)
async def safe_unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Hide internal exception details from API clients."""

    del request, exc
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
                    "An unexpected error occurred. Please try again later."
                ),
            }
        },
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render the dashboard with an explicit API-mode label."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_mode": API_MODE},
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Return a non-sensitive health response."""

    return {
        "status": "ok",
        "service": "ledgerlock-api",
        "environment": APP_ENV,
    }
