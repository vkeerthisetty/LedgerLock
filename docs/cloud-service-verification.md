# Cloud Service Verification & IAM Notes
**Owner:** Jaanvi (Cloud Security Engineer)
**Environment Status:** Local simulation and Floci-GCP 0.13.0 integration verified on 28 November 2026. This is local emulator evidence, not real Google Cloud evidence.

## 1. Service Verification Matrix
| Service / Control | Required Operation | Status | Evidence / Implementation |
| :--- | :--- | :--- | :--- |
| **Firestore** | Create synthetic record & read ordered by `sequence` | **Verified in Floci** | Official Firestore client wrote and read a unique synthetic document through `localhost:4588`; persisted across FastAPI restart (`evidence/floci/integration-output.txt`) |
| **Cloud KMS** | Asymmetric checkpoint signing & public-key verification | **Verified in Floci** | EC P-256 key version (`ledgerlock-keyring/checkpoint-signer/v1`) signed a SHA-256 digest; retrieved PEM public key verified it (`evidence/floci/integration-output.txt`) |
| **Cloud Logging** | Record redacted security events | **Verified in Floci** | Structured allowlisted event written and read back; unapproved/secret fields absent (`evidence/floci/integration-output.txt`) |
| **IAM Least Privilege (`ledgerlock-sa`)** | Runtime service account with `datastore.user`, `cloudkms.signerVerifier`, `logging.logWriter` | **Configured / Unverified Live** | Defined in `infra/deploy_cloud_run.sh` (`evidence/IAM-01/iam-cloudrun-verification.txt`); Floci is credential-free so runtime IAM enforcement is not verified |
| **Cloud Run Deployment** | Containerized deployment (`--no-allow-unauthenticated`) with explicit env vars | **Prepared / Unverified Live** | `infra/Dockerfile` & `infra/deploy_cloud_run.sh` prepared with `$GCP_PROJECT_ID` guard and `asia-south1` region; not deployed live due to no billing-enabled GCP sandbox |
| **Cloud Logging Retention & Access** | Bucket retention policies & IAM read restrictions | **Untested Live** | Requires live GCP Cloud Logging administration; not simulated in Floci |

## Floci-GCP execution boundary

- Floci-GCP runs locally on port `4588` and requires no cloud login or real credentials.
- `docker-compose.floci.yml` provides persistent disposable emulator state.
- `infra/bootstrap_floci.py` creates only local KMS resources using an insecure localhost gRPC channel.
- `tests/test_floci_integration.py` is opt-in through `RUN_FLOCI_INTEGRATION=true`.
- Reproduction evidence is stored in `evidence/floci/integration-output.txt`.
- FastAPI cloud mode uses Firestore records and KMS checkpoints and passed a restart-persistence test.
- Public Render deliberately keeps cloud mode disabled and remains in-memory.
- FastAPI cloud mode writes allowlisted event-creation, verification and checkpoint security metadata to Cloud Logging.

## 2. Least-Privilege IAM Design (`ledgerlock-sa`)
- `roles/datastore.user`: Read/write synthetic audit documents in Firestore.
- `roles/cloudkms.signerVerifier`: Sign chain checkpoints and retrieve public key for verification without exporting private key material.
- `roles/logging.logWriter`: Write structured, redacted security events to Cloud Logging.
- Cloud Run deployed in `asia-south1` with `--no-allow-unauthenticated` and explicit `--set-env-vars` (`USE_CLOUD_SERVICES`, `GCP_PROJECT_ID`, `GCP_REGION`, `FIRESTORE_COLLECTION`, `KMS_KEY_RING`, `KMS_KEY_NAME`, `KMS_KEY_VERSION`, `CLOUD_LOG_NAME`) so IAM authentication and explicit cloud resource bindings are enforced at deploy time (`evidence/IAM-01/iam-cloudrun-verification.txt`).
- **Limitation:** Static verification of `infra/deploy_cloud_run.sh` confirms configuration intent only and does **not** prove live GCP IAM enforcement.

## 3. Key-Handling Controls (Test T04)
- Private keys are never written to audit records, environment templates, logs, or Git commits.
- `LedgerStorageAdapter.save_record()` explicitly blocks any record containing `PRIVATE KEY` markers.
