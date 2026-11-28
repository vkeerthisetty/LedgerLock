import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from storage.firestore_adapter import LedgerStorageAdapter
from signing.kms_adapter import CheckpointSignerAdapter

spec = importlib.util.spec_from_file_location("cloud_logger", ROOT / "logging/cloud_logger.py")
cloud_logger_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloud_logger_mod)
SecurityLoggerAdapter = cloud_logger_mod.SecurityLoggerAdapter

FORBIDDEN = [
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "private_key",
    "_ephemeral_hmac_key",
    "client_secret",
]


def run_t04_check() -> str:
    temp = Path("data/t04_test_records.json")
    temp.unlink(missing_ok=True)
    storage = LedgerStorageAdapter(use_cloud=False, local_path=str(temp))
    signer = CheckpointSignerAdapter(use_cloud=False)
    logger = SecurityLoggerAdapter(use_cloud=False, local_log_path="logs/t04_verification.jsonl")

    rec = {
        "record_id": "rec-synth-001",
        "sequence": 1,
        "timestamp": "2026-11-27T13:30:00Z",
        "event_type": "LEDGER_INIT",
        "actor_id": "actor-synth-01",
        "action": "CREATE_RECORD",
        "resource_id": "res-synth-01",
        "outcome": "SUCCESS",
        "request_id": "req-t04-001",
        "previous_hash": "0" * 64,
        "current_hash": "a1b2c3d4e5f6" * 5 + "abcd",
    }
    ckpt = signer.sign_checkpoint(rec["current_hash"])
    verified, verify_msg = signer.verify_checkpoint(rec["current_hash"], ckpt["signature"])
    rec["checkpoint_algorithm"] = ckpt["algorithm"]
    rec["checkpoint_key_id"] = ckpt["key_id"]
    rec["checkpoint_signature"] = ckpt["signature"]

    storage.save_record(rec)
    records = storage.read_chain()
    leaks = [m for m in FORBIDDEN if m.lower() in json.dumps(records).lower()]
    passed = (len(leaks) == 0) and verified

    logger.log_event({
        "event_type": "T04_PRIVATE_KEY_INSPECTION",
        "outcome": "PASS" if passed else "FAIL",
        "request_id": "req-t04-001",
        "verification_result": "NO_PRIVATE_KEY_FOUND" if passed else "LEAK_DETECTED",
    })

    report_lines = [
        "Test ID: T04",
        "Phase: After-Fix",
        "Environment: Windows Local Workstation (Python 3 / Local Simulation Adapter)",
        "Date: 2026-11-28",
        f"T04 Private Key Inspection Result: {'PASS' if passed else 'FAIL'}",
        f"Signature Verification Status: {verify_msg}",
        f"Records Inspected: {len(records)} | Forbidden Markers Found: {len(leaks)}",
        f"Stored Key Reference (Public/Non-Secret Only): {records[0]['checkpoint_key_id']}",
    ]
    output = "\n".join(report_lines)
    print(output)
    temp.unlink(missing_ok=True)
    return output


if __name__ == "__main__":
    run_t04_check()
