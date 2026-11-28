# LedgerLock Release Criteria

## Functional requirements

- [x] Frontend loads without unexpected errors.
- [x] Mock and live modes are visibly distinguished.
- [x] Synthetic audit events can be submitted and validated.
- [x] Backend assigns authoritative IDs, timestamps, sequences and hashes.
- [x] Records can be retrieved in sequence order.
- [x] Verification checks the complete available chain.
- [x] Invalid input produces controlled responses.
- [ ] Active records survive Render or application restart.

## Cryptographic requirements

- [x] Canonical hashing behavior is implemented and tested.
- [x] SHA-256 links and sequence integrity are verified.
- [x] Local HMAC-SHA256 checkpoint format is documented.
- [x] Local checkpoint creation requires administrator authorization.
- [x] Local checkpoint verification is tested.
- [x] Signing secrets are absent from frontend and repository content.
- [ ] Cloud KMS asymmetric signing and public-key verification are observed.

## Cloud and infrastructure requirements

- [x] Cloud/local adapters default safely to local simulation.
- [x] Render deployment is live and health-checked.
- [x] Cloud claims are labelled verified, simulated or untested.
- [ ] Floci workspace and service availability are verified.
- [ ] Firestore persistence and concurrency behavior are verified.
- [ ] Least-privilege runtime identity is verified.
- [ ] Cloud Logging delivery, redaction and access are verified.
- [ ] Cloud Run is verified if required by the assigned environment.

## Security requirements

- [x] Server-side input validation is tested.
- [x] Checkpoint creation rejects missing or incorrect authorization.
- [x] Safe HTTP, validation and unexpected-error handling is implemented.
- [x] Local logs filter fields and sensitive-looking values.
- [x] Browser code contains no credentials or signing material.
- [x] Evidence uses synthetic data.
- [ ] A complete end-user authentication model is implemented.

## Evidence requirements

- [x] T01 untouched chain.
- [x] T02 modified record.
- [x] T03 missing/reordered record.
- [x] T04 private-key material inspection.
- [x] T05 tamper-evidence claim boundary.
- [x] T06 controlled unexpected error.
- [x] T07 sensitive-data inspection for local scope.
- [x] T08 complete implemented regression.
- [ ] T01-T08 repeated after live cloud integration.

## Documentation requirements

- [x] Architecture and data-flow documents exist.
- [x] Threat model and permission matrix exist.
- [x] API contract matches the implemented local API.
- [x] Findings register and integration checklist are current.
- [x] Security Assessment Report and evidence index exist.
- [x] README records setup and limitations.
- [x] Demonstration plan matches current behavior.

## Demonstration requirements

- [x] Public Render workflow was smoke-tested with synthetic data.
- [x] Successful chain verification was observed.
- [x] Controlled tampering is covered by repeatable tests.
- [x] Local checkpoint and unauthorized request cases are tested.
- [x] Claims distinguish local simulation from cloud verification.
- [ ] All five members complete a timed final rehearsal.

## Release decision

**Controlled local/Render demonstration: approved with conditions.**

Conditions: use synthetic data, state that active records are disposable, label HMAC as local, and do not claim Firestore, Cloud KMS, Cloud Run, Cloud Logging or Floci verification.

**Complete cloud release: not approved.**

Reviewer: Keerthi, Project Coordinator

Review date: 28 November 2026

Tested source baseline: `9b195ed`
