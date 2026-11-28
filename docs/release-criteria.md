# LedgerLock Release Criteria

## 1. Functional Requirements

- [x] Frontend loads without unexpected errors.
- [x] Mock and live modes are visibly distinguished.
- [x] Synthetic audit events can be submitted and validated.
- [x] Backend assigns authoritative IDs, timestamps, sequences and hashes.
- [x] Records can be retrieved in sequence order.
- [x] Verification checks the complete available chain.
- [x] Invalid input produces controlled responses.
- [ ] Active records survive Render or application restart.

## 2. Cryptographic Requirements

- [x] Canonical hashing behavior is implemented and tested.
- [x] SHA-256 links and sequence integrity are verified.
- [x] Local HMAC-SHA256 checkpoint format is documented.
- [x] Local checkpoint creation requires administrator authorization.
- [x] Local checkpoint verification is tested.
- [x] Signing secrets are absent from frontend and repository content.
- [ ] Cloud KMS asymmetric signing and public-key verification are observed.

A successful frontend demonstration, verification run or active deployment alone does not establish that the complete ledger and cloud security implementation is operational.

## 3. Cloud and Infrastructure Requirements

- [x] Cloud/local adapters default safely to local simulation.
- [x] Render deployment is live and health-checked.
- [x] Cloud claims are labelled verified, simulated or untested.
- [ ] Floci workspace and service availability are verified.
- [ ] Firestore persistence and concurrency behavior are verified.
- [ ] Least-privilege runtime identity is verified.
- [ ] Cloud Logging delivery, redaction and access are verified.
- [ ] Cloud Run is verified if required by the assigned environment.

## 4. Security Requirements

- [x] Server-side input validation is tested.
- [x] Checkpoint creation rejects missing or incorrect authorization.
- [x] Safe HTTP, validation and unexpected-error handling is implemented.
- [x] Local logs filter fields and sensitive-looking values.
- [x] Browser code contains no credentials or signing material.
- [x] Evidence uses synthetic data.
- [ ] A complete end-user authentication model is implemented.
- [ ] Storage and signing permissions are reviewed.
- [ ] Complete authorization coverage across implemented routes is reviewed.

## 5. Evidence Requirements

The following test cases are recorded as completed for the tested local scope:

- [x] T01 – Untouched chain.
- [x] T02 – Modified record.
- [x] T03 – Missing or reordered record.
- [x] T04 – Private-key material inspection.
- [x] T05 – Tamper-evidence claim boundary.
- [x] T06 – Controlled unexpected error.
- [x] T07 – Sensitive-data inspection for local scope.
- [x] T08 – Complete implemented regression.
- [ ] T01–T08 repeated after live cloud integration.

Test results apply to the source revision and environment in which they were executed. They do not independently establish production security or untested cloud functionality.

## 6. Environment and Deployment Requirements

### 6.1 Local Development

- [x] Default mock mode is visibly labelled.
- [x] Mock mode is not represented as live cryptographic verification.
- [x] Local environment files and credentials are excluded from Git.
- [ ] Local setup instructions work from a clean environment.

### 6.2 Floci Verification

- [ ] Floci verification workflow is documented by its owner.
- [ ] Verification source revision is recorded.
- [ ] Test commands and results are recorded.
- [ ] Synthetic data is used.
- [ ] Verification results are not presented as proof of unrelated cloud integrations.
- [ ] The relationship between Floci verification and Render deployment is documented.

### 6.3 Active Render Deployment

- [x] Public Render workflow was smoke-tested with synthetic data.
- [ ] Deployed source revision is recorded and confirmed.
- [ ] Actual API mode is confirmed.
- [ ] Available routes are checked.
- [ ] Health endpoint is checked.
- [ ] Environment configuration is reviewed without exposing secret values.
- [ ] Any connected cloud integrations are independently verified.
- [ ] Deployment evidence matches the claims made in the README and demonstration.

An active Render deployment must not be treated as proof of Firestore or KMS integration.

## 7. Documentation Requirements

- [x] Architecture and data-flow documents exist.
- [x] Threat model and permission matrix exist.
- [x] API contract documents the intended interface and implementation boundaries.
- [x] Findings register and integration checklist exist.
- [x] Security Assessment Report and evidence index exist.
- [x] README records setup and limitations.
- [x] Demonstration plan reflects documented implementation boundaries.
- [ ] Documentation is reviewed against the final integrated implementation.
- [ ] Planned features are distinguished from implemented features.

## 8. Demonstration Requirements

- [x] Demonstration uses synthetic data.
- [x] Successful chain verification is covered by testing.
- [x] Controlled tampering is covered by repeatable tests.
- [x] Local checkpoint and unauthorized request cases are tested.
- [x] Claims distinguish local simulation from cloud verification.
- [ ] All five team members complete a timed final rehearsal.
- [ ] No credentials, private keys or sensitive information appear in screenshots.
- [ ] Demonstration claims match actual implementation evidence.
- [ ] Floci verification and Render deployment are described accurately.

## 9. Release Decision

**Controlled local/Render demonstration: Approved with conditions.**

Conditions:

- Use synthetic data only.
- State clearly that active records may be disposable.
- Label HMAC checkpoint functionality as local.
- Distinguish implemented functionality from simulation and planned integrations.
- Do not claim Firestore, Cloud KMS, Cloud Run, Cloud Logging or Floci verification without supporting evidence.

**Complete cloud release: Not approved.**

Outstanding release requirements include durable storage, cloud signing, cloud logging, permission verification, authentication review and deployment evidence.

## 10. Final Review

Reviewer: Keerthi, Project Coordinator

Review date: 28 November 2026

Tested source baseline: `9b195ed` (incoming version's recorded baseline; confirm before release)

Outstanding issues: Cloud integration, durable storage, authentication and deployment verification.

Approval status: Controlled demonstration approved with conditions; complete cloud release not approved.

## 11. Final Principle

A feature is considered verified only when its implementation has been reviewed and supporting test evidence is available.

A mock demonstration, planned feature or untested integration must not be represented as a verified security capability.

Verification in Floci and deployment on Render are separate activities and require separate supporting evidence.
