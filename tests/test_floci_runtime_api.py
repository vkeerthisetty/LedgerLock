"""Opt-in end-to-end FastAPI test against local Floci-GCP."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid

import httpx
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_FLOCI_RUNTIME", "false").lower() != "true",
    reason="Set RUN_FLOCI_RUNTIME=true after starting Floci-GCP.",
)

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _start_api(environment: dict[str, str], port: int) -> subprocess.Popen:
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise AssertionError(f"API exited during startup:\n{output}")
        try:
            response = httpx.get(f"{base_url}/api/health", timeout=1.0)
            if response.status_code == 200:
                return process
        except httpx.HTTPError:
            pass
        time.sleep(0.1)

    _stop_api(process)
    raise AssertionError("API did not become ready in time.")


def _stop_api(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def test_cloud_mode_persists_records_and_kms_checkpoint_across_restart():
    suffix = uuid.uuid4().hex[:10]
    admin_token = f"synthetic-admin-{suffix}"
    environment = os.environ.copy()
    environment.update(
        {
            "LEDGERLOCK_ENV": "floci-test",
            "LEDGERLOCK_API_MODE": "live",
            "LEDGERLOCK_ADMIN_TOKEN": admin_token,
            "USE_CLOUD_SERVICES": "true",
            "GCP_PROJECT_ID": "floci-local",
            "GOOGLE_CLOUD_PROJECT": "floci-local",
            "GCP_REGION": "us-central1",
            "FLOCI_GCP_ENDPOINT": "http://localhost:4588",
            "FIRESTORE_EMULATOR_HOST": "localhost:4588",
            "FIRESTORE_COLLECTION": f"audit_ledger_runtime_{suffix}",
            "KMS_KEY_RING": "ledgerlock-keyring",
            "KMS_KEY_NAME": "checkpoint-signer",
            "KMS_KEY_VERSION": "1",
        }
    )
    event = {
        "event_type": "verification",
        "actor_id": "synthetic-reviewer",
        "action": "verified Floci runtime integration",
        "resource_id": "synthetic-ledger",
        "outcome": "success",
    }

    first_port = _free_port()
    first_process = _start_api(environment, first_port)
    first_url = f"http://127.0.0.1:{first_port}"
    try:
        first = httpx.post(f"{first_url}/api/events", json=event, timeout=10.0)
        second = httpx.post(f"{first_url}/api/events", json=event, timeout=10.0)
        assert first.status_code == 201
        assert second.status_code == 201
        assert [first.json()["sequence"], second.json()["sequence"]] == [1, 2]
        request_ids = {first.json()["request_id"], second.json()["request_id"]}

        denied = httpx.post(f"{first_url}/api/checkpoints", timeout=10.0)
        assert denied.status_code == 403

        checkpoint = httpx.post(
            f"{first_url}/api/checkpoints",
            headers={"x-admin-token": admin_token},
            timeout=10.0,
        )
        assert checkpoint.status_code == 200
        assert checkpoint.json()["latest_sequence"] == 2

        verified = httpx.post(f"{first_url}/api/verify", timeout=10.0)
        assert verified.status_code == 200
        assert verified.json()["valid"] is True
        assert verified.json()["checkpoint_valid"] is True
    finally:
        _stop_api(first_process)

    second_port = _free_port()
    second_process = _start_api(environment, second_port)
    second_url = f"http://127.0.0.1:{second_port}"
    try:
        restored = httpx.get(f"{second_url}/api/ledger", timeout=10.0)
        assert restored.status_code == 200
        assert restored.json()["count"] == 2
        assert restored.json()["checkpoint"]["status"] == "available"

        verified = httpx.post(f"{second_url}/api/verify", timeout=10.0)
        assert verified.json()["valid"] is True
        assert verified.json()["checkpoint_valid"] is True

        third = httpx.post(f"{second_url}/api/events", json=event, timeout=10.0)
        assert third.status_code == 201
        assert third.json()["sequence"] == 3
        request_ids.add(third.json()["request_id"])

        stale = httpx.post(f"{second_url}/api/verify", timeout=10.0)
        assert stale.json()["valid"] is True
        assert stale.json()["checkpoint_valid"] is False

        listed_logs = httpx.post(
            "http://localhost:4588/v2/entries:list",
            json={"resourceNames": ["projects/floci-local"]},
            timeout=10.0,
        )
        listed_logs.raise_for_status()
        runtime_logs = [
            item.get("jsonPayload", {})
            for item in listed_logs.json().get("entries", [])
            if item.get("jsonPayload", {}).get("request_id") in request_ids
        ]
        assert len(runtime_logs) == 3
        assert all(item["event_type"] == "EVENT_CREATE" for item in runtime_logs)
        assert all("actor_id" not in item for item in runtime_logs)
        assert admin_token not in listed_logs.text
    finally:
        _stop_api(second_process)
