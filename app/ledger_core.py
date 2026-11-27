
"""Core hash-chain ledger for LedgerLock."""

from __future__ import annotations

import hashlib
import json
import threading
import uuid

from datetime import datetime, timezone
from typing import Any


GENESIS_HASH = "0" * 64


def canonical_json(data: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON bytes."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def calculate_hash(record: dict[str, Any]) -> str:
    """Calculate SHA-256 without including the record's own hash."""
    hash_data = dict(record)
    hash_data.pop("current_hash", None)

    return hashlib.sha256(canonical_json(hash_data)).hexdigest()


class AuditLedger:
    """Store audit records and verify their hash chain."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def add_event(self, event: dict[str, str]) -> dict[str, Any]:
        """Create a record with server-generated metadata."""
        with self._lock:
            previous_hash = (
                self._records[-1]["current_hash"]
                if self._records
                else GENESIS_HASH
            )

            record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z"),
                "sequence": len(self._records) + 1,
                "request_id": str(uuid.uuid4()),
                "event_type": event["event_type"],
                "actor_id": event["actor_id"],
                "action": event["action"],
                "resource_id": event["resource_id"],
                "outcome": event["outcome"],
                "previous_hash": previous_hash,
            }

            record["current_hash"] = calculate_hash(record)
            self._records.append(record)

            return dict(record)

    def get_records(self) -> list[dict[str, Any]]:
        """Return copies of records in ascending sequence order."""
        with self._lock:
            return [dict(record) for record in self._records]

    @staticmethod
    def verify_records(
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Check sequence numbers, previous hashes and record hashes."""
        previous_hash = GENESIS_HASH

        for index, record in enumerate(records):
            sequence = record.get("sequence")

            if sequence != index + 1:
                return {
                    "valid": False,
                    "checked_records": index + 1,
                    "failed_sequence": sequence,
                    "message": f"Integrity verification failed at sequence {sequence}.",
                }

            if record.get("previous_hash") != previous_hash:
                return {
                    "valid": False,
                    "checked_records": index + 1,
                    "failed_sequence": sequence,
                    "message": f"Integrity verification failed at sequence {sequence}.",
                }

            if record.get("current_hash") != calculate_hash(record):
                return {
                    "valid": False,
                    "checked_records": index + 1,
                    "failed_sequence": sequence,
                    "message": f"Integrity verification failed at sequence {sequence}.",
                }

            previous_hash = record["current_hash"]

        return {
            "valid": True,
            "checked_records": len(records),
            "failed_sequence": None,
            "message": "Chain verified.",
        }
