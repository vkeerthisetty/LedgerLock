# Integration Checklist

## Verified status - 28 November 2026

| Area | Status | Evidence or limitation |
|---|---|---|
| Frontend and FastAPI | Integrated and deployed | Render smoke test and API tests |
| Hash chain and sequence verification | Verified locally | T01-T03 |
| Protected local checkpoint | Verified locally | API and checkpoint tests |
| Safe errors and redacted local logging | Verified locally | T06-T07 |
| Repository key-material controls | Verified for tracked scope | T04 and safety scan |
| Cloud/local adapters | Verified in local simulation | `tests/test_cloud_adapters.py` |
| Firestore active storage | Integrated in Floci cloud mode | FastAPI records survived an API restart; public Render remains in-memory |
| Cloud KMS | Integrated in Floci cloud mode | Active checkpoint EC P-256 sign/public-key verify and restart recovery |
| Cloud Logging | Integrated in Floci cloud mode | Sanitized event, verification and checkpoint metadata written/read |
| Cloud Run and IAM | Not verified | Render is current host |
| Floci | Verified locally | Floci-GCP 0.13.0; Firestore, KMS and Logging running |
| Report and evidence | Updated | Final cloud revision still pending |

## Contract readiness

- [x] Frontend and backend use the documented event, ledger, verify, checkpoint and health routes.
- [x] Local checkpoint status and error shapes are documented.
- [x] Cloud adapters are disabled unless explicitly enabled.
- [x] Safe errors and permitted local log fields are reviewed.
- [x] Firestore/KMS adapter interfaces are verified against Floci.
- [ ] IAM contract is approved by all owners.

## Integrated build

- [x] Frontend works in labelled mock and live modes.
- [x] Backend tests cover canonical hashes, sequences and links.
- [x] Create, list, verify, checkpoint and health flows pass locally.
- [x] Render create, list, verify, health and unauthorized-checkpoint smoke tests pass.
- [x] Complete local regression and safety scan pass.
- [x] Cloud claims are labelled simulated or unverified.
- [x] Firestore provides transactional ordering and API-restart persistence in Floci.
- [x] KMS signs and verifies the persisted checkpoint in Floci cloud mode.
- [x] Floci logging write/read and redaction test passes.
- [ ] Least-privilege IAM enforcement tests pass.
- [ ] Final report/evidence are repeated on the cloud-integrated revision.
- [ ] A timed five-member rehearsal is recorded.

## Integration order for remaining work

1. Verify IAM enforcement and Cloud Run runtime if required.
2. Review authorization, errors, logs and secret handling.
3. Repeat T01-T08 on the final reviewed revision.
