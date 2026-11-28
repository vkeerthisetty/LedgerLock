## Cloud Operations & Environment Limitations
**Author:** Jaanvi (Cloud Security Engineer)

### Cloud Services & Architecture Readiness
LedgerLock abstracts storage (`storage/firestore_adapter.py`), checkpoint signing (`signing/kms_adapter.py`), and security logging (`logging/cloud_logger.py`) behind service adapters controlled by `USE_CLOUD_SERVICES`. Container and IAM deployment configurations (`infra/Dockerfile`, `infra/deploy_cloud_run.sh`) define least-privilege access via `ledgerlock-sa` (`roles/datastore.user`, `roles/cloudkms.signerVerifier`, `roles/logging.logWriter`), `--no-allow-unauthenticated`, and explicit runtime environment variables in `asia-south1`.

### Verified Operations in Floci-GCP vs. Unverified Live Cloud
- **Verified in Local Floci-GCP (`localhost:4588`):** Transactional Firestore record persistence across FastAPI restarts, asymmetric `EC_SIGN_P256_SHA256` Cloud KMS checkpoint signing and PEM public-key verification (addressing **F-003** in cloud mode), allowlisted/redacted Cloud Logging write/read, and private-key absence enforcement (Test **T04**) are verified in `evidence/floci/integration-output.txt`.
- **Configured but Unverified Live (`IAM-01`):** `ledgerlock-sa` IAM bindings and Cloud Run `--no-allow-unauthenticated` deployment are prepared in `infra/deploy_cloud_run.sh` (`evidence/IAM-01/iam-cloudrun-verification.txt`), but runtime IAM policy enforcement is **not** exercised by credential-free Floci and remains unverified until an authorised, billing-enabled GCP project is available.
- **Public Render Boundary:** Public Render intentionally keeps `USE_CLOUD_SERVICES=false` and operates in disposable in-memory mode with local HMAC checkpoints.

### Key Handling & Assumptions
- **Zero Private Key Storage (T04):** Stored audit records contain only public key identifiers and signatures, verified in `evidence/T04/key-material-scan.txt`, `evidence/after-fix/T04_after_fix_no_private_key.txt`, and `evidence/floci/integration-output.txt`.
- **Assumptions:** When deployed to an assigned GCP sandbox, LedgerLock assumes Cloud KMS prevents private key export and GCP IAM policies prevent non-admin actors from modifying Firestore documents directly outside the API workflow.
