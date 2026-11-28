
"""Development checkpoint creation and verification for LedgerLock."""

import hashlib
import hmac
import json
from typing import Mapping, Sequence


def _secret_bytes(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode("utf-8")

    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("Checkpoint secret must contain at least 32 bytes.")

    return secret


def _checkpoint_payload(checkpoint: Mapping) -> bytes:
    data = {
        "schema_version": checkpoint["schema_version"],
        "latest_sequence": checkpoint["latest_sequence"],
        "latest_hash": checkpoint["latest_hash"],
        "key_version": checkpoint["key_version"],
    }

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def create_checkpoint(
    records: Sequence[Mapping],
    secret: str | bytes,
    key_version: str = "development-v1",
) -> dict:
    """Create an authenticated checkpoint for the current ledger tip."""

    key = _secret_bytes(secret)

    if records:
        latest = records[-1]
        sequence = latest.get("sequence")
        record_hash = latest.get("current_hash")

        if not isinstance(sequence, int) or not isinstance(record_hash, str):
            raise ValueError("Latest ledger record is invalid.")
    else:
        sequence = None
        record_hash = None

    checkpoint = {
        "schema_version": 1,
        "latest_sequence": sequence,
        "latest_hash": record_hash,
        "key_version": key_version,
    }

    checkpoint["signature"] = hmac.new(
        key,
        _checkpoint_payload(checkpoint),
        hashlib.sha256,
    ).hexdigest()

    checkpoint["algorithm"] = "HMAC-SHA256"
    return checkpoint


def verify_checkpoint(
    records: Sequence[Mapping],
    checkpoint: Mapping,
    secret: str | bytes,
) -> bool:
    """Check the checkpoint signature and whether the ledger ends at that tip."""

    try:
        key = _secret_bytes(secret)

        if checkpoint.get("algorithm") != "HMAC-SHA256":
            return False

        expected_signature = hmac.new(
            key,
            _checkpoint_payload(checkpoint),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            expected_signature,
            checkpoint["signature"],
        ):
            return False

        if records:
            latest = records[-1]
            actual_sequence = latest.get("sequence")
            actual_hash = latest.get("current_hash")
        else:
            actual_sequence = None
            actual_hash = None

        return (
            actual_sequence == checkpoint["latest_sequence"]
            and actual_hash == checkpoint["latest_hash"]
        )

    except (KeyError, TypeError, ValueError):
        return False
