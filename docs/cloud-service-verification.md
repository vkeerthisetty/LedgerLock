# Cloud Service Verification & IAM Notes
**Owner:** Jaanvi (Cloud Security Engineer)
**Environment Status:** Local simulation and Floci-GCP 0.13.0 integration verified on 28 November 2026. This is local emulator evidence, not real Google Cloud evidence.

## 1. Service Verification Matrix
| Service | Required Operation | Status | Evidence / Implementation |
| :--- | :--- | :--- | :--- |
| **Firestore** | Create synthetic record & read ordered by `sequence` | **Verified in Floci** | Official Firestore client wrote and read a unique synthetic document through `localhost:4588` |
| **Cloud KMS** | Asymmetric checkpoint signing & public-key verification | **Verified in Floci** | EC P-256 key version signed a SHA-256 digest; retrieved public key verified it |
| **Cloud Run** | Containerized deployment (`--no-allow-unauthenticated`) | **Prepared / Unverified Live** | `infra/Dockerfile` & `infra/deploy_cloud_run.sh` prepared with `$GCP_PROJECT_ID` validation; not deployed due to no live GCP sandbox |
| **Cloud Logging** | Record redacted security events | **Verified in Floci** | Structured event written and read back; unapproved field absent |

## Floci-GCP execution boundary

- Floci-GCP runs locally on port `4588` and requires no cloud login or real credentials.
- `docker-compose.floci.yml` provides persistent disposable emulator state.
- `infra/bootstrap_floci.py` creates only local KMS resources using an insecure localhost gRPC channel.
- `tests/test_floci_integration.py` is opt-in through `RUN_FLOCI_INTEGRATION=true`.
- Reproduction evidence is stored in `evidence/floci/integration-output.txt`.
- The active FastAPI application remains in-memory; adapter verification is not application integration.

## 2. Least-Privilege IAM Design (`ledgerlock-sa`)
- `roles/datastore.user`: Read/write synthetic audit documents in Firestore.
- `roles/cloudkms.signerVerifier`: Sign chain checkpoints and retrieve public key for verification without exporting private key material.
- `roles/logging.logWriter`: Write structured, redacted security events to Cloud Logging.
- Cloud Run deployed with `--no-allow-unauthenticated` so IAM authentication is enforced by default.

## 3. Key-Handling Controls (Test T04)
- Private keys are never written to audit records, environment templates, logs, or Git commits.
- `LedgerStorageAdapter.save_record()` explicitly blocks any record containing `PRIVATE KEY` markers.
