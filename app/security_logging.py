
"""Security-focused logging utilities for LedgerLock."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from logging.cloud_logger import SecurityLoggerAdapter


logger = logging.getLogger("ledgerlock.security")

SAFE_TEXT = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

ALLOWED_FIELDS = {
    "event_type",
    "outcome",
    "correlation_id",
    "request_id",
    "verification_result",
    "failed_sequence",
    "error_category",
}


def configure_security_logger() -> logging.Logger:
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


def sanitise_log_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Accept only approved fields with restricted values."""

    safe_data: dict[str, Any] = {}

    for key, value in data.items():
        if key not in ALLOWED_FIELDS:
            continue

        if not isinstance(value, (str, int, float, bool)):
            continue

        if isinstance(value, str):
            if not SAFE_TEXT.fullmatch(value):
                continue

            if re.search(
                r"password|secret|token|credential|private.?key|bearer",
                value,
                re.IGNORECASE,
            ):
                continue

        safe_data[key] = value

    return safe_data


def log_security_event(**fields: Any) -> None:
    """Write an allowlisted security event using the configured adapter."""

    safe_data = sanitise_log_fields(fields)
    safe_data["timestamp"] = datetime.now(timezone.utc).isoformat()

    try:
        cloud_logger = SecurityLoggerAdapter(
            use_cloud=(
                __import__("os").getenv(
                    "USE_CLOUD_SERVICES", "false"
                ).lower() == "true"
            )
        )
        cloud_logger.log_event(safe_data)
    except Exception:
        # Never expose logging-service failures or sensitive data.
        logger.warning(
            json.dumps(
                {
                    "event_type": "security_logging_failure",
                    "outcome": "controlled_error",
                },
                sort_keys=True,
            )
        )


configure_security_logger()
