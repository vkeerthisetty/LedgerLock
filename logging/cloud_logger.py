import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_LOG_FIELDS = {
    "event_type", "timestamp", "outcome", "request_id",
    "verification_result", "failed_sequence", "error_category", "mode"
}

SENSITIVE_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"(private_key|secret|password|token|authorization|api_key|bearer)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
]


def sanitize_log_value(value):
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            return "[REDACTED_SENSITIVE_VALUE]"
    return text[:256]


class SecurityLoggerAdapter:
    def __init__(self, use_cloud: bool = False, local_log_path: str = "logs/security_events.jsonl"):
        self.use_cloud = use_cloud and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        self.mode = "GCP_CLOUD_LOGGING" if self.use_cloud else "LOCAL_SIMULATION"
        self.local_log_path = Path(local_log_path)
        if not self.use_cloud:
            self.local_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, payload: dict) -> dict:
        clean = {
            k: sanitize_log_value(v)
            for k, v in payload.items()
            if k in ALLOWED_LOG_FIELDS
        }
        clean["timestamp"] = datetime.now(timezone.utc).isoformat()
        clean["mode"] = self.mode
        if self.use_cloud:
            from google.cloud import logging as cloud_logging
            cloud_logging.Client().logger(os.getenv("CLOUD_LOG_NAME", "ledgerlock-audit-events")).log_struct(clean)
        else:
            with self.local_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(clean) + "\n")
        return clean
