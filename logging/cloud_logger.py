import json, os
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_LOG_FIELDS = {
    "event_type", "timestamp", "outcome", "request_id",
    "verification_result", "failed_sequence", "error_category", "mode"
}

class SecurityLoggerAdapter:
    def __init__(self, use_cloud: bool = False, local_log_path: str = "logs/security_events.jsonl"):
        self.use_cloud = use_cloud and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        self.mode = "GCP_CLOUD_LOGGING" if self.use_cloud else "LOCAL_SIMULATION"
        self.local_log_path = Path(local_log_path)
        if not self.use_cloud:
            self.local_log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, payload: dict) -> dict:
        clean = {k: v for k, v in payload.items() if k in ALLOWED_LOG_FIELDS}
        clean["timestamp"] = datetime.now(timezone.utc).isoformat()
        clean["mode"] = self.mode
        if self.use_cloud:
            from google.cloud import logging as cloud_logging
            cloud_logging.Client().logger(os.getenv("CLOUD_LOG_NAME", "ledgerlock-audit-events")).log_struct(clean)
        else:
            with self.local_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(clean) + "\n")
        return clean
