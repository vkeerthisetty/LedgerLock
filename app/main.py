
"""FastAPI entry point for the LedgerLock frontend foundation."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException


BASE_DIR = Path(__file__).resolve().parent
API_MODE = os.getenv("LEDGERLOCK_API_MODE", "mock").strip().lower()

if API_MODE not in {"mock", "live"}:
    raise RuntimeError("LEDGERLOCK_API_MODE must be either 'mock' or 'live'.")

app = FastAPI(
    title="LedgerLock",
    description="Tamper-evident audit-ledger demonstration frontend",
    version="0.1.0",
)


@app.exception_handler(StarletteHTTPException)
async def safe_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Return controlled HTTP errors without exposing internal details."""

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


@app.exception_handler(RequestValidationError)
async def safe_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return safe validation information without submitted values."""

    fields = list(
        dict.fromkeys(
            str(error["loc"][-1])
            for error in exc.errors()
            if error.get("loc") and isinstance(error["loc"][-1], str)
        )
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "fields": fields,
            }
        },
    )


@app.exception_handler(Exception)
async def safe_unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Hide unexpected internal errors from API clients."""

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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
        "service": "ledgerlock-frontend",
        "api_mode": API_MODE,
    }
