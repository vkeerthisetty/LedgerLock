# Integration Checklist

Keerthi maintains this checklist; each specialist owner supplies their own code, tests, run instructions, and evidence.

## Contract readiness

- [ ] Jyoshitha approves the data flow, assets, trust boundaries, and release criteria.
- [ ] Syed and Keerthi agree on every route, field, status code, and error shape in `docs/api-contract.md`.
- [ ] Jaanvi documents the Firestore, KMS, Logging, and deployment interfaces.
- [ ] Omar reviews input limits, safe errors, data minimisation, and permitted log fields.

## Component readiness

- [ ] Frontend works in labelled mock mode.
- [ ] Backend unit tests cover canonical records, sequence rules, hash links, and verification.
- [ ] Firestore adapter preserves stable sequence order and handles concurrent creation safely.
- [ ] KMS adapter signs the approved checkpoint content and supports verification.
- [ ] Access and logging tests confirm that secrets and complete sensitive payloads are absent.

## Integrated build

- [ ] The frontend runs with `LEDGERLOCK_API_MODE=live`.
- [ ] Create, list, verify, checkpoint, and health flows match the agreed contract.
- [ ] T01–T07 have baseline and after-fix evidence from their owners.
- [ ] T08 passes from a clean setup using the documented instructions.
- [ ] Every cloud claim is labelled verified, simulated, or untested.
- [ ] The report, README, evidence index, and demonstration use the same final release revision.
- [ ] A tested local backup is available for the demonstration.
