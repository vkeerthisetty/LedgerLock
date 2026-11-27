import importlib.util
import json
from pathlib import Path
import pytest

from storage.firestore_adapter import LedgerStorageAdapter
from signing.kms_adapter import CheckpointSignerAdapter

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cloud_logger", ROOT / "logging/cloud_logger.py")
cloud_logger_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud_logger_mod)
SecurityLoggerAdapter = cloud_logger_mod.SecurityLoggerAdapter


def test_disabled_cloud_fallback_enforced_when_env_false(monkeypatch):
    monkeypatch.setenv("USE_CLOUD_SERVICES", "false")
    storage = LedgerStorageAdapter(use_cloud=True, local_path="data/test_fallback.json")
    signer = CheckpointSignerAdapter(use_cloud=True)
    logger = SecurityLoggerAdapter(use_cloud=True, local_log_path="logs/test_fallback.jsonl")

    assert storage.use_cloud is False
    assert storage.mode == "LOCAL_SIMULATION"
    assert signer.use_cloud is False
    assert signer.mode == "LOCAL_SIMULATION"
    assert logger.use_cloud is False
    assert logger.mode == "LOCAL_SIMULATION"
    Path("data/test_fallback.json").unlink(missing_ok=True)


def test_local_storage_persists_ordered_by_sequence_and_blocks_private_keys(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    storage = LedgerStorageAdapter(use_cloud=False, local_path=str(ledger_file))

    storage.save_record({"sequence": 2, "record_id": "r2", "current_hash": "hash2"})
    storage.save_record({"sequence": 1, "record_id": "r1", "current_hash": "hash1"})

    chain = storage.read_chain()
    assert [r["sequence"] for r in chain] == [1, 2]

    with pytest.raises(ValueError, match="SECURITY_BLOCK"):
        storage.save_record({"sequence": 3, "leak": "-----BEGIN PRIVATE KEY-----abc"})


def test_signing_verification_and_invalid_signature_rejection():
    signer = CheckpointSignerAdapter(use_cloud=False)
    signed = signer.sign_checkpoint("checkpoint-hash-123")

    assert signed["algorithm"] == "HMAC-SHA256"
    assert signed["key_id"] == "local-sim://hmac-sha256-ephemeral"
    assert "rsa" not in signed["key_id"].lower()

    ok, msg = signer.verify_checkpoint("checkpoint-hash-123", signed["signature"])
    assert ok is True
    assert "PASSED" in msg

    bad_ok, bad_msg = signer.verify_checkpoint("checkpoint-hash-123", "0" * 64)
    assert bad_ok is False
    assert "FAILED" in bad_msg

    tampered_ok, _ = signer.verify_checkpoint("tampered-hash", signed["signature"])
    assert tampered_ok is False


def test_safe_logging_filters_fields_and_redacts_sensitive_values(tmp_path):
    log_file = tmp_path / "sec.jsonl"
    logger = SecurityLoggerAdapter(use_cloud=False, local_log_path=str(log_file))

    entry = logger.log_event({
        "event_type": "AUTH_CHECK",
        "outcome": "FAIL",
        "request_id": "req-99",
        "error_category": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdef123456.sig1234567890",
        "verification_result": "-----BEGIN PRIVATE KEY-----secret",
        "unapproved_secret_field": "super-secret-password",
    })

    assert "unapproved_secret_field" not in entry
    assert entry["error_category"] == "[REDACTED_SENSITIVE_VALUE]"
    assert entry["verification_result"] == "[REDACTED_SENSITIVE_VALUE]"

    persisted = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert "unapproved_secret_field" not in persisted
    assert persisted["error_category"] == "[REDACTED_SENSITIVE_VALUE]"
