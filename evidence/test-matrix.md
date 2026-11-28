# LedgerLock Test Evidence Matrix

- Evidence date: 28 November 2026
- Tested source baseline: Floci integration revision based on parent `a0e9cdc`
- Environment: Python 3.12.14 on Windows; Render public deployment; Floci-GCP 0.13.0
- Evidence owner: Keerthi, Project Coordinator
- Data classification: synthetic demonstration records only

| ID | Test | Status | Evidence | Limitation / next action |
|---|---|---|---|---|
| T01 | Untouched chain verifies | PASS | `evidence/T01/verification-output.txt` | Available in-memory chain |
| T02 | Changed event is detected | PASS | `evidence/T02/verification-output.txt` | Controlled disposable copy |
| T03 | Missing or reordered event is detected | PASS | `evidence/T03/verification-output.txt` | Local removal and reversal cases |
| T04 | Private-key material is absent | PASS | `evidence/T04/key-material-scan.txt`; `evidence/floci/integration-output.txt` | Floci KMS keeps the private key inside the local emulator; real GCP not inspected |
| T05 | Report distinguishes tamper evidence from immutability | PASS | `evidence/T05/claim-boundary.md` | Cloud durability remains pending |
| T06 | Controlled unexpected error is safe and logged | PASS | `evidence/T06/verification-output.txt` | Local handler/log only |
| T07 | Source, output and local logs contain no observed secrets | PASS WITH LIMITATIONS | `evidence/T07/repository-scan.txt`; `evidence/floci/integration-output.txt` | Floci Logging write/read verified; real GCP retention and access not inspected |
| T08 | Complete implemented test set is reproducible | PASS FOR IMPLEMENTED SCOPE | `evidence/T08/regression-output.txt`; `evidence/floci/integration-output.txt` | Cloud Run runtime, IAM enforcement and real GCP excluded |

## Interpretation

PASS applies only to the stated scope and evidence. Local Floci-GCP tests establish Firestore persistence through a FastAPI restart, active KMS checkpoint signing/verification, checkpoint freshness, and sanitized runtime security-log write/read. They do not establish a real GCP deployment, Cloud Run runtime or IAM enforcement.
