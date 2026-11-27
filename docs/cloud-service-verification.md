# Cloud Service Verification & IAM Notes
**Owner:** Jaanvi (Cloud Security Engineer)  
**Environment Status:** Local Simulation Adapters Verified (`USE_CLOUD_SERVICES=false`); Cloud Run/KMS/Firestore deployment scripts prepared in `infra/`.

## 1. Service Verification Matrix
| Service | Required Operation | Status | Evidence / Implementation |
| :--- | :--- | :--- | :--- |
| **Firestore** | Create synthetic record & read ordered by `sequence` | **Simulated (Local Adapter)** | `storage/firestore_adapter.py` (`LOCAL_SIMULATION` mode); SDK path ready when `USE_CLOUD_SERVICES=true` |
| **Cloud KMS** | Asymmetric checkpoint signing & verification | **Simulated (Local Adapter)** | `signing/kms_adapter.py` (`LOCAL_SIMULATION` mode); stores only public key reference and signature |
| **Cloud Run** | Containerized deployment & smoke test | **Prepared / Unverified Live** | `infra/Dockerfile` & `infra/deploy_cloud_run.sh` prepared; not deployed due to no live GCP sandbox |
| **Cloud Logging** | Record redacted security events | **Simulated (Local Adapter)** | `logging/cloud_logger.py` enforces strict field allowlist (`ALLOWED_LOG_FIELDS`) |

## 2. Least-Privilege IAM Design (`ledgerlock-sa`)
- `roles/datastore.user`: Read/write synthetic audit documents in Firestore.
- `roles/cloudkms.signerVerifier`: Sign checkpoints and verify signatures without exporting private key material.
- `roles/logging.logWriter`: Write structured, redacted security events to Cloud Logging.

## 3. Key-Handling Controls (Test T04)
- Private keys are never written to audit records, environment templates, logs, or Git commits.
- `LedgerStorageAdapter.save_record()` explicitly blocks any record containing `PRIVATE KEY` markers.
