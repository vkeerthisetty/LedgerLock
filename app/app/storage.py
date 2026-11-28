"""Common storage interface for LedgerLock."""

from typing import Any, Protocol


class LedgerStorage(Protocol):
    """Interface shared by local and cloud ledger storage."""

    def add_event(self, event: dict[str, str]) -> dict[str, Any]:
        """Persist an event and return its complete audit record."""
        ...

    def get_records(self) -> list[dict[str, Any]]:
        """Return all records in ascending sequence order."""
        ...

    def get_checkpoint(self) -> dict[str, Any] | None:
        """Return the latest persisted checkpoint, if available."""
        ...

    def save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        """Persist the latest trusted checkpoint."""
        ...
