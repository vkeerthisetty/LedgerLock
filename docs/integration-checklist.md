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
| Firestore active storage | Not integrated | Adapter exists; FastAPI still uses memory |
| Cloud KMS | Verified in Floci | EC P-256 asymmetric sign/public-key verify round trip |
| Cloud Logging | Verified in Floci | Sanitized structured event write/read round trip |
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
- [ ] Firestore provides durable, concurrency-safe ordering.
- [ ] KMS signs and verifies the persisted checkpoint.
- [x] Floci logging write/read and redaction test passes.
- [ ] Least-privilege IAM enforcement tests pass.
- [ ] Final report/evidence are repeated on the cloud-integrated revision.
- [ ] A timed five-member rehearsal is recorded.

## Integration order for remaining work

1. Connect the verified Firestore, KMS and Logging adapters to FastAPI without breaking local mode.
2. Verify IAM enforcement and Cloud Run runtime if required.
3. Review authorization, errors, logs and secret handling.
4. Repeat T01-T08 and update this checklist, report and demo.
