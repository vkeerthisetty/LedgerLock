# LedgerLock Test Evidence Matrix

- Evidence date: 28 November 2026
- Tested source baseline: `9b195ed`
- Environment: Python 3.12.14 on Windows; Render public deployment
- Evidence owner: Keerthi, Project Coordinator
- Data classification: synthetic demonstration records only

| ID | Test | Status | Evidence | Limitation / next action |
|---|---|---|---|---|
| T01 | Untouched chain verifies | PASS | `evidence/T01/verification-output.txt` | Available in-memory chain |
| T02 | Changed event is detected | PASS | `evidence/T02/verification-output.txt` | Controlled disposable copy |
| T03 | Missing or reordered event is detected | PASS | `evidence/T03/verification-output.txt` | Local removal and reversal cases |
| T04 | Private-key material is absent | PASS | `evidence/T04/key-material-scan.txt` | No live KMS configuration inspected |
| T05 | Report distinguishes tamper evidence from immutability | PASS | `evidence/T05/claim-boundary.md` | Cloud durability remains pending |
| T06 | Controlled unexpected error is safe and logged | PASS | `evidence/T06/verification-output.txt` | Local handler/log only |
| T07 | Source, output and local logs contain no observed secrets | PASS WITH LIMITATIONS | `evidence/T07/repository-scan.txt` | Live Cloud Logging not inspected |
| T08 | Complete implemented test set is reproducible | PASS FOR IMPLEMENTED SCOPE | `evidence/T08/regression-output.txt` | Live cloud operations excluded |

## Interpretation

PASS applies only to the stated scope and evidence. Adapter tests and local simulation do not establish Firestore, Cloud KMS, Cloud Run, Cloud Logging or Floci operation. Those claims remain pending until tested in the assigned environment.
