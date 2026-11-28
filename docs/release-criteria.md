
# LedgerLock – Release Criteria

## 1. Purpose

This document defines the security, functional, integration and documentation conditions that must be satisfied before LedgerLock is recommended for release.

A successful frontend demonstration, verification run or active deployment alone does not establish that the complete ledger and cloud security implementation is operational.

## 2. Functional Requirements

- [ ] Frontend loads without unexpected errors.
- [ ] Mock mode is visibly labelled.
- [ ] Synthetic audit events can be submitted.
- [ ] Backend validates submitted data.
- [ ] Backend assigns authoritative record metadata.
- [ ] Records are stored using the configured storage adapter.
- [ ] Ledger records can be retrieved in sequence order.
- [ ] Verification checks the complete available chain.
- [ ] Verification results are displayed safely.
- [ ] Invalid input produces controlled error responses.

## 3. Cryptographic Requirements

- [ ] Canonical record format is documented.
- [ ] SHA-256 hashing is implemented and tested.
- [ ] Previous-hash relationships are verified.
- [ ] Sequence integrity is checked.
- [ ] Trusted checkpoint format is documented.
- [ ] Checkpoint signing is implemented where required.
- [ ] Checkpoint signature verification is tested.
- [ ] Private signing keys are not exposed to the frontend or repository.
- [ ] Checkpoint creation requires authorization.

## 4. Cloud Security Requirements

- [ ] Firestore integration is verified, if included in the release.
- [ ] Cloud KMS integration is verified, if included in the release.
- [ ] Firestore permissions follow least privilege.
- [ ] KMS permissions are restricted to required signing and public-key retrieval operations.
- [ ] Cloud Logging accepts only allowlisted, sanitized fields.
- [ ] Service identities use least-privilege permissions.
- [ ] Credentials are not committed to the repository.
- [ ] Storage and signing permissions are reviewed.
- [ ] Cloud operations are labelled accurately as verified, simulated or untested.

## 5. Security Requirements

- [ ] Backend input validation is reviewed.
- [ ] Unauthorized operations are restricted.
- [ ] Safe error handling is implemented.
- [ ] Error responses do not expose exception details or internal paths.
- [ ] Logs do not expose secrets or unnecessary sensitive data.
- [ ] Complete event payloads are not logged unnecessarily.
- [ ] Browser code contains no private keys or service credentials.
- [ ] Only synthetic test data is used in evidence.
- [ ] Security findings are reviewed and documented.

## 6. Environment and Deployment Requirements

### 6.1 Local Development

- [ ] Local setup instructions work from a clean environment.
- [ ] Default mock mode is visibly labelled.
- [ ] Mock mode is not represented as live cryptographic verification.
- [ ] Local environment files and credentials are excluded from Git.

### 6.2 Floci Verification

- [ ] Floci verification workflow is documented by its owner.
- [ ] Verification source revision is recorded.
- [ ] Test commands and results are recorded.
- [ ] Synthetic data is used.
- [ ] Verification results are not presented as proof of unrelated cloud integrations.
- [ ] The relationship between Floci verification and Render deployment is documented.

### 6.3 Active Render Deployment

- [ ] Active deployment is confirmed.
- [ ] Deployed source revision is recorded.
- [ ] Actual API mode is confirmed.
- [ ] Available routes are checked.
- [ ] Health endpoint is checked.
- [ ] Environment configuration is reviewed without exposing secret values.
- [ ] Any connected cloud integrations are independently verified.
- [ ] Deployment evidence matches the claims made in the README and demonstration.

An active Render deployment must not be treated as proof of Firestore or KMS integration.

## 7. Test Evidence Requirements

- [ ] T01 – Untouched chain verifies successfully.
- [ ] T02 – Modified stored event is detected.
- [ ] T03 – Removed or reordered event causes integrity verification failure within the tested scope.
- [ ] T04 – Private-key inspection is performed.
- [ ] T05 – Tamper evidence is distinguished from immutability.
- [ ] T06 – Controlled unexpected error is handled safely.
- [ ] T07 – Source, output and logs are checked for secrets and unnecessary sensitive data.
- [ ] T08 – Full test suite can be repeated from a clean setup.

Each test must have recorded evidence and an accurate result.

Tests that have not been run must remain marked as pending.

Evidence must identify the tested source revision and environment wherever possible.

## 8. Documentation Requirements

- [ ] Architecture diagram is available.
- [ ] Data-flow document distinguishes local, Floci and Render.
- [ ] Threat model is reviewed.
- [ ] Findings register is updated.
- [ ] API contract reflects the implemented interface.
- [ ] Integration checklist is updated.
- [ ] Evidence index is available.
- [ ] README describes setup and limitations accurately.
- [ ] Planned features are distinguished from implemented features.

## 9. Demonstration Requirements

- [ ] Demonstration uses synthetic data.
- [ ] Mock and live modes are clearly distinguished.
- [ ] Successful verification is demonstrated where implemented.
- [ ] A controlled tampering scenario is demonstrated where implemented.
- [ ] Verification failure is explained.
- [ ] No credentials, private keys or sensitive information appear in screenshots.
- [ ] Demonstration claims match actual implementation evidence.
- [ ] Floci verification and Render deployment are described accurately.

## 10. Release Decision

The project should not be described as fully integrated or cryptographically verified until the relevant implementation and tests have been completed.

Release recommendation:

- Approved
- Approved with documented limitations
- Not approved

Outstanding issues:

Reviewer:

Review date:

Project revision:

## 11. Final Principle

A feature is considered verified only when its implementation has been reviewed and supporting test evidence is available.

A mock demonstration, planned feature or untested integration must not be represented as a verified security capability.

Verification in Floci and deployment on Render are separate activities and require separate supporting evidence.
