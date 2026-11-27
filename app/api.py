
"""LedgerLock backend API."""

import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.ledger_core import AuditLedger
from app.checkpoint import create_checkpoint, verify_checkpoint

router = APIRouter()
ledger = AuditLedger()

checkpoint: Optional[dict] = None

CHECKPOINT_SECRET = os.getenv("LEDGERLOCK_CHECKPOINT_SECRET", "")
ADMIN_TOKEN = os.getenv("LEDGERLOCK_ADMIN_TOKEN", "")


class EventInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(min_length=1, max_length=50)
    actor_id: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=200)
    resource_id: str = Field(min_length=1, max_length=100)
    outcome: str = Field(min_length=1, max_length=50)


@router.post("/api/events", status_code=201)
def add_event(event: EventInput):
    """Add an event to the audit ledger."""
    return ledger.add_event(event.model_dump())


@router.get("/api/ledger")
def get_ledger():
    """Return records in sequence order."""
    records = ledger.get_records()

    return {
        "records": records,
        "count": len(records),
        "latest_sequence": records[-1]["sequence"] if records else None,
        "checkpoint": {
            "status": "available" if checkpoint else "unavailable",
            "key_version": checkpoint.get("key_version") if checkpoint else None,
        },
    }


@router.post("/api/verify")
def verify_ledger():
    """Verify the hash chain and, when available, its checkpoint."""
    records = ledger.get_records()
    result = AuditLedger.verify_records(records)

    checkpoint_valid = False

    if checkpoint and CHECKPOINT_SECRET:
        checkpoint_valid = verify_checkpoint(
            records, checkpoint, CHECKPOINT_SECRET
        )

    return {
        "valid": result["valid"],
        "checked_records": result["checked_records"],
        "failed_sequence": result["failed_sequence"],
        "checkpoint_valid": checkpoint_valid,
        "message": (
            "Chain and checkpoint verified."
            if result["valid"] and checkpoint_valid
            else result["message"]
            if not result["valid"]
            else "Chain verified; trusted checkpoint unavailable or invalid."
        ),
    }


@router.post("/api/checkpoints")
def make_checkpoint(x_admin_token: str = Header(default="")):
    """Create a trusted checkpoint; requires administrator configuration."""
    global checkpoint

    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Not authorised.")

    if len(CHECKPOINT_SECRET) < 32:
        raise HTTPException(
            status_code=503,
            detail="Checkpoint signing is not configured.",
        )

    try:
        checkpoint = create_checkpoint(
            ledger.get_records(),
            CHECKPOINT_SECRET,
        )
    except ValueError:
        raise HTTPException(
            status_code=409,
            detail="Cannot checkpoint an invalid ledger.",
        )

    return {
        "status": "created",
        "latest_sequence": checkpoint["latest_sequence"],
        "key_version": checkpoint["key_version"],
    }
