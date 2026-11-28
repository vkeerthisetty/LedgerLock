
"""Opt-in integration tests against the local Floci-GCP emulator."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import uuid

import httpx
import pytest

from signing.kms_adapter import CheckpointSignerAdapter
from storage.firestore_adapter import LedgerStorageAdapter


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_FLOCI_INTEGRATION", "false").lower() != "true",
    reason="Set RUN_FLOCI_INTEGRATION=true after starting Floci-GCP.",
)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "cloud_logger", ROOT / "logging" / "cloud_logger.py"
)
cloud_logger_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud_logger_mod)
SecurityLoggerAdapter = cloud_logger_mod.SecurityLoggerAdapter


def test_floci_firestore_kms_and_logging_round_trip(monkeypatch):
    suffix = uuid.uuid4().hex[:10]

    monkeypatch.setenv("USE_CLOUD_SERVICES", "true")
    monkeypatch.setenv("GCP_PROJECT_ID", "floci-local")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "floci-local")
    monkeypatch.setenv("GCP_REGION", "us-central1")
    monkeypatch.setenv("FLOCI_GCP_ENDPOINT", "http://localhost:4588")
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "localhost:4588")
    monkeypatch.setenv("FIRESTORE_COLLECTION", f"audit_ledger_{suffix}")

    health = httpx.get(
        "http://localhost:4588/_floci-gcp/health",
        timeout=10.0,
    )
    health.raise_for_status()

    services = health.json()["services"]
    assert services["firestore"] == "running"
    assert services["kms"] == "running"
    assert services["logging"] == "running"

    # Firestore record storage and retrieval.
    storage = LedgerStorageAdapter(use_cloud=True)

    record = {
        "sequence": 1,
        "record_id": f"floci-{suffix}",
        "current_hash": "a" * 64,
    }

    result = storage.save_record(record)
    assert result["mode"] == "GCP_FIRESTORE"
    assert storage.read_chain() == [record]

    # Verify records can be recovered using a fresh adapter.
    restarted_storage = LedgerStorageAdapter(use_cloud=True)
    restored_records = restarted_storage.read_chain()

    assert restored_records == [record]
    assert restored_records[0]["record_id"] == f"floci-{suffix}"

    # Firestore checkpoint storage and recovery.
    checkpoint = {
        "latest_sequence": 1,
        "latest_hash": "a" * 64,
        "signature": f"test-signature-{suffix}",
        "mode": "GCP_CLOUD_KMS",
    }

    storage.save_checkpoint(checkpoint)

    restarted_storage = LedgerStorageAdapter(use_cloud=True)
    restored_checkpoint = restarted_storage.get_checkpoint()

    assert restored_checkpoint == checkpoint

    # Cloud KMS signing and verification.
    signer = CheckpointSignerAdapter(use_cloud=True)

    signed = signer.sign_checkpoint("b" * 64)

    ok, message = signer.verify_checkpoint(
        "b" * 64,
        signed["signature"],
    )

    assert signed["mode"] == "GCP_CLOUD_KMS"
    assert ok is True
    assert "PASSED" in message

    # Cloud Logging submission.
    logger = SecurityLoggerAdapter(use_cloud=True)

    entry = logger.log_event(
        {
            "event_type": "FLOCI_INTEGRATION_TEST",
            "outcome": "PASS",
            "request_id": f"floci-{suffix}",
        }
    )

    assert entry["mode"] == "GCP_CLOUD_LOGGING"

    listed = httpx.post(
        "http://localhost:4588/v2/entries:list",
        json={"resourceNames": ["projects/floci-local"]},
        timeout=10.0,
    )
    listed.raise_for_status()

    matching_entries = [
        item["jsonPayload"]
        for item in listed.json().get("entries", [])
        if item.get("jsonPayload", {}).get("request_id") == f"floci-{suffix}"
    ]

    assert len(matching_entries) == 1
    assert matching_entries[0]["event_type"] == "FLOCI_INTEGRATION_TEST"
    assert "unapproved_secret_field" not in matching_entries[0]
