"""Local in-memory storage adapter for LedgerLock."""

from typing import Any

from app.ledger_core import AuditLedger
from app.storage import LedgerStorage

class LocalLedgerStorage:
    """Use the existing in-memory ledger for local development."""

    def __init__(self) -> None:
        self.ledger = AuditLedger()
        self._checkpoint: dict[str, Any] | None = None

    def add_event(self, event: dict[str, str]) -> dict[str, Any]:
        return self.ledger.add_event(event)

    def get_records(self) -> list[dict[str, Any]]:
        return self.ledger.get_records()

    def get_checkpoint(self) -> dict[str, Any] | None:
        return dict(self._checkpoint) if self._checkpoint else None

    def save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        self._checkpoint = dict(checkpoint)
