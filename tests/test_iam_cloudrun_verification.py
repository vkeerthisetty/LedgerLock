from pathlib import Path


def test_deploy_script_enforces_least_privilege_iam_and_authenticated_cloud_run():
    script = Path("infra/deploy_cloud_run.sh").read_text(encoding="utf-8")
    assert "GCP_PROJECT_ID" in script
    assert "floci-local" in script
    assert "ledgerlock-sa" in script
    assert "roles/datastore.user" in script
    assert "roles/cloudkms.signerVerifier" in script
    assert "roles/logging.logWriter" in script
    assert "roles/owner" not in script
    assert "roles/editor" not in script
    assert "--no-allow-unauthenticated" in script
    assert "--allow-unauthenticated" not in script.replace("--no-allow-unauthenticated", "")


def test_env_example_has_approved_floci_defaults_and_no_secrets():
    env_text = Path(".env.example").read_text(encoding="utf-8")
    assert "GCP_PROJECT_ID=floci-local" in env_text
    assert "GCP_REGION=us-central1" in env_text
    assert "FIRESTORE_EMULATOR_HOST=localhost:4588" in env_text
    assert "FIRESTORE_COLLECTION=audit_ledger_floci" in env_text
    assert "KMS_KEY_RING=ledgerlock-keyring" in env_text
    assert "KMS_KEY_NAME=checkpoint-signer" in env_text
    assert "BEGIN PRIVATE KEY" not in env_text


def test_floci_verification_evidence_is_present_and_sanitized():
    ev_path = Path("evidence/floci-verification/T05_iam_cloudrun_verification.txt")
    assert ev_path.exists()
    content = ev_path.read_text(encoding="utf-8")
    assert len(content.strip()) > 100
    for forbidden in ["BEGIN PRIVATE KEY", "client_secret", "private_key_id", "AIza", "ya29."]:
        assert forbidden not in content
