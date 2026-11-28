## Cloud Operations & Environment Limitations
**Author:** Jaanvi (Cloud Security Engineer)

### Cloud Services & Architecture Readiness
LedgerLock abstracts storage (`storage/firestore_adapter.py`), checkpoint signing (`signing/kms_adapter.py`), and security logging (`logging/cloud_logger.py`) behind service adapters controlled by `USE_CLOUD_SERVICES`. Container and IAM deployment configurations (`infra/Dockerfile`, `infra/deploy_cloud_run.sh`) enforce least-privilege access via `ledgerlock-sa`.

### Verified Operations vs. Local Simulations
- **Local Simulation Verified:** Ordered record persistence, sequence-sorted retrieval, checkpoint signing/verification, allowlisted security logging, and private-key absence enforcement (Test **T04**) were executed locally using clearly labelled `LOCAL_SIMULATION` adapters.
- **Unverified Live Cloud Operations:** Live GCP Firestore, Cloud KMS, Cloud Run, and Cloud Logging were not executed against a live GCP project during this sprint and remain documented as environment limitations.

### Key Handling & Assumptions
- **Zero Private Key Storage (T04):** Stored audit records contain only public key identifiers and signatures, verified in `evidence/after-fix/T04_after_fix_no_private_key.txt`.
- **Assumptions:** When deployed to an assigned GCP sandbox, LedgerLock assumes Cloud KMS prevents private key export and IAM policies prevent non-admin actors from modifying Firestore documents directly outside the API workflow.
