
"""LedgerLock backend API."""

import json
import os
from typing import Any, Literal

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.ledger_core import AuditLedger
from app.checkpoint import create_checkpoint, verify_checkpoint

router = APIRouter()

CHECKPOINT_SECRET = os.getenv("LEDGERLOCK_CHECKPOINT_SECRET", "")
ADMIN_TOKEN = os.getenv("LEDGERLOCK_ADMIN_TOKEN", "")


class EventInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    event_type: Literal[
        "access",
        "configuration",
        "verification",
        "authentication",
    ]
    actor_id: str = Field(min_length=1, max_length=64)
    action: str = Field(min_length=1, max_length=120)
    resource_id: str = Field(min_length=1, max_length=64)
    outcome: Literal["success", "denied", "controlled_error"]


def _checkpoint_payload(checkpoint: dict[str, Any]) -> str:
    payload = {
        "schema_version": checkpoint["schema_version"],
        "latest_sequence": checkpoint["latest_sequence"],
        "latest_hash": checkpoint["latest_hash"],
        "key_version": checkpoint["key_version"],
    }

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def _get_records(request: Request) -> list[dict[str, Any]]:
    return request.app.state.storage.get_records()


def _get_checkpoint(request: Request):
    return request.app.state.checkpoint


@router.post("/api/events", status_code=201)
def add_event(event: EventInput, request: Request):
    try:
        return request.app.state.storage.add_event(event.model_dump())
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The ledger storage service is unavailable.",
        )


@router.get("/api/ledger")
def get_ledger(request: Request):
    try:
        records = _get_records(request)
        checkpoint = _get_checkpoint(request)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The ledger storage service is unavailable.",
        )

    return {
        "records": records,
        "count": len(records),
        "latest_sequence": (
            records[-1]["sequence"] if records else None
        ),
        "checkpoint": {
            "status": "available" if checkpoint else "unavailable",
            "key_version": (
                checkpoint.get("key_version") if checkpoint else None
            ),
        },
    }


@router.post("/api/verify")
def verify_ledger(request: Request):
    try:
        records = _get_records(request)
        checkpoint = _get_checkpoint(request)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The ledger verification service is unavailable.",
        )

    result = AuditLedger.verify_records(records)
    checkpoint_valid = False

    if checkpoint and result["valid"]:
        latest = records[-1] if records else None

        checkpoint_matches_chain = (
            checkpoint.get("latest_sequence")
            == (latest["sequence"] if latest else None)
            and checkpoint.get("latest_hash")
            == (latest["current_hash"] if latest else None)
        )

        if checkpoint_matches_chain:
            if checkpoint.get("mode") == "GCP_CLOUD_KMS":
                try:
                    configured_version = os.getenv(
                        "KMS_KEY_VERSION", "1"
                    )

                    if str(checkpoint.get("key_version")) == str(
                        configured_version
                    ):
                        signer = request.app.state.signer
                        payload = _checkpoint_payload(checkpoint)

                        checkpoint_valid, _ = signer.verify_checkpoint(
                            payload,
                            checkpoint.get("signature", ""),
                        )
                except Exception:
                    checkpoint_valid = False

            elif CHECKPOINT_SECRET:
                checkpoint_valid = verify_checkpoint(
                    records,
                    checkpoint,
                    CHECKPOINT_SECRET,
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
def make_checkpoint(
    request: Request,
    x_admin_token: str = Header(default=""),
):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Not authorised.",
        )

    try:
        records = _get_records(request)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The ledger storage service is unavailable.",
        )

    if not AuditLedger.verify_records(records)["valid"]:
        raise HTTPException(
            status_code=409,
            detail="Cannot checkpoint an invalid ledger.",
        )

    signer = request.app.state.signer

    try:
        if signer.use_cloud:
            latest = records[-1] if records else None

            checkpoint = {
                "schema_version": 1,
                "latest_sequence": (
                    latest["sequence"] if latest else None
                ),
                "latest_hash": (
                    latest["current_hash"] if latest else None
                ),
                "key_version": os.getenv("KMS_KEY_VERSION", "1"),
                "mode": "GCP_CLOUD_KMS",
            }

            signed = signer.sign_checkpoint(
                _checkpoint_payload(checkpoint)
            )

            checkpoint.update(signed)

        else:
            if len(CHECKPOINT_SECRET) < 32:
                raise HTTPException(
                    status_code=503,
                    detail="Checkpoint signing is not configured.",
                )

            checkpoint = create_checkpoint(
                records,
                CHECKPOINT_SECRET,
            )

            checkpoint["mode"] = "LOCAL_SIMULATION"

        request.app.state.storage.save_checkpoint(checkpoint)
        request.app.state.checkpoint = checkpoint

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Checkpoint signing service is unavailable.",
        )

    return {
        "status": "created",
        "latest_sequence": checkpoint["latest_sequence"],
        "key_version": checkpoint["key_version"],
    }
