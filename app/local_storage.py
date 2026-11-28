
"""Local in-memory storage adapter for LedgerLock."""

import json
import os
from pathlib import Path
from typing import Any

from app.ledger_core import AuditLedger


class LocalLedgerStorage:
    """Use an in-memory ledger with persistent local checkpoints."""

    def __init__(self) -> None:
        self.ledger = AuditLedger()
        self.mode = "LOCAL_SIMULATION"

        self.checkpoint_path = Path(
            os.getenv(
                "LEDGERLOCK_LOCAL_CHECKPOINT_PATH",
                "data/local_checkpoint.json",
            )
        )

        self.checkpoint_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._checkpoint: dict[str, Any] | None = None

        if self.checkpoint_path.exists():
            self._checkpoint = json.loads(
                self.checkpoint_path.read_text(encoding="utf-8")
            )

    def add_event(self, event: dict[str, str]) -> dict[str, Any]:
        return self.ledger.add_event(event)

    def get_records(self) -> list[dict[str, Any]]:
        return self.ledger.get_records()

    def get_checkpoint(self) -> dict[str, Any] | None:
        return dict(self._checkpoint) if self._checkpoint else None

    def save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        self.checkpoint_path.write_text(
            json.dumps(checkpoint, indent=2),
            encoding="utf-8",
        )

        self._checkpoint = dict(checkpoint)
