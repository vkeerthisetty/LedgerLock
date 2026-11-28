# Cloud Service Verification, IAM & Cloud Run Security Review
**Owner:** Jaanvi (Cloud Security Engineer)  
**Scope:** Floci Workspace Security Review + IAM & Cloud Run Deployment Verification

## 1. Approved Floci Workspace & Endpoint Configuration
- **Project ID:** `floci-local`
- **Region:** `us-central1`
- **Shared Floci Endpoint:** `http://localhost:4588`
- **Firestore Emulator Host:** `localhost:4588` (Collection: `audit_ledger_floci`)
- **Cloud KMS Key Resource:** `ledgerlock-keyring` / `checkpoint-signer` / version `1` (`EC_SIGN_P256_SHA256`)

## 2. Service & Operation Verification Matrix
| Service | Operation | Status | Verification Notes |
| :--- | :--- | :--- | :--- |
| **Firestore** | Synthetic write, `sequence`-ordered read, persistence across FastAPI restarts | **Verified** | Verified in Floci (`localhost:4588`, collection `audit_ledger_floci`) and FastAPI adapter wiring |
| **Cloud KMS** | `EC P-256` key creation (v1), SHA-256 digest signing, `get_public_key` verification | **Verified** | Verified in Floci without exporting private key material |
| **Cloud Logging** | Sanitized structured log write & read | **Verified** | Verified in Floci with allowlisted fields and sensitive-value redaction |
| **IAM & Identity** | Dedicated `ledgerlock-sa` with `datastore.user`, `cloudkms.signerVerifier`, `logging.logWriter` | **Unsupported (Local) / Documented Design** | Floci is credential-free and does not enforce IAM policy bindings locally |
| **Cloud Run** | Containerized deployment with `--no-allow-unauthenticated` | **Untested (Live)** | Scripted in `infra/deploy_cloud_run.sh` with `floci-local` guard; requires live GCP project |
| **Cloud Logging** | Log bucket retention & IAM read access control | **Untested (Live)** | Requires live GCP Cloud Logging administration |

## 3. Runtime Service Identity & Least-Privilege IAM Design
- **Service Identity:** `ledgerlock-sa@<GCP_PROJECT_ID>.iam.gserviceaccount.com`
- **Assigned Roles (Least Privilege):**
  1. `roles/datastore.user` — Read and write tamper-evident ledger documents in Firestore.
  2. `roles/cloudkms.signerVerifier` — Sign checkpoint digests and fetch the public key for verification; denies key export or admin deletion.
  3. `roles/logging.logWriter` — Emit structured audit/security logs; denies reading or deleting historical log buckets.
- **No Static Key Files:** Designed for attached Cloud Run runtime service identity with zero `.env` secrets or downloaded service-account JSON keys.

## 4. Cloud Run Deployment Security Verification
- `infra/deploy_cloud_run.sh` enforces:
  - Non-empty `${GCP_PROJECT_ID}` validation and explicit rejection of `floci-local` so emulator settings cannot be deployed accidentally.
  - Dedicated `--service-account "${SA_EMAIL}"` attachment.
  - `--no-allow-unauthenticated` so unauthenticated public invocations are blocked at the Cloud Run IAM layer.

## 5. Known Limitations
- **Credential-Free Emulator:** Floci validates API shapes and persistence locally, but does not enforce Google Cloud IAM permissions, service-account impersonation, or Cloud Logging retention policies.
- **Live Cloud Run Runtime:** Cold-start behavior, HTTPS ingress, and IAM invoker (`roles/run.invoker`) enforcement remain untested against live Google Cloud until a billing-enabled GCP sandbox is provisioned.
