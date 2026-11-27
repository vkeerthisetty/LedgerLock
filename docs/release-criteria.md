
# LedgerLock – Release Criteria

## 1. Purpose

This document defines the security, functional, integration and documentation conditions that must be satisfied before LedgerLock is recommended for release.

A successful frontend demonstration alone does not establish that the complete ledger and cloud security implementation is operational.

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

## 4. Cloud Security Requirements

- [ ] Firestore integration is verified, if included in the release.
- [ ] Cloud KMS integration is verified, if included in the release.
- [ ] Service identities use least-privilege permissions.
- [ ] Credentials are not committed to the repository.
- [ ] Storage and signing permissions are reviewed.
- [ ] Cloud operations are labelled accurately as verified, simulated or untested.

## 5. Security Requirements

- [ ] Backend input validation is reviewed.
- [ ] Unauthorized operations are restricted.
- [ ] Safe error handling is implemented.
- [ ] Logs do not expose secrets or unnecessary sensitive data.
- [ ] Browser code contains no private keys or service credentials.
- [ ] Only synthetic test data is used in evidence.
- [ ] Security findings are reviewed and documented.

## 6. Test Evidence Requirements

- [ ] T01 – Untouched chain verifies successfully.
- [ ] T02 – Modified stored event is detected.
- [ ] T03 – Removed or reordered event causes integrity verification failure.
- [ ] T04 – Stored records are checked for private-key material.
- [ ] T05 – Tamper evidence is distinguished from immutability.
- [ ] T06 – Unexpected errors are handled safely.
- [ ] T07 – Secrets and unnecessary sensitive data are checked.
- [ ] T08 – Full test suite can be repeated from a clean setup.

Each test must have recorded evidence and an accurate result.

Tests that have not been run must remain marked as pending.

## 7. Documentation Requirements

- [ ] Architecture diagram is available.
- [ ] Data-flow document is complete.
- [ ] Threat model is reviewed.
- [ ] Findings register is updated.
- [ ] API contract reflects the implemented interface.
- [ ] Integration checklist is updated.
- [ ] Evidence index is available.
- [ ] README describes setup and limitations accurately.

## 8. Demonstration Requirements

- [ ] Demonstration uses synthetic data.
- [ ] Mock and live modes are clearly distinguished.
- [ ] Successful verification is demonstrated.
- [ ] A controlled tampering scenario is demonstrated where implemented.
- [ ] Verification failure is explained.
- [ ] No credentials, private keys or sensitive information appear in screenshots.
- [ ] Demonstration claims match actual implementation evidence.

## 9. Release Decision

The project should not be described as fully integrated or cryptographically verified until the relevant implementation and tests have been completed.

Release recommendation:

- Approved
- Approved with documented limitations
- Not approved

Outstanding issues:

Reviewer:

Review date:

Project revision:

## 10. Final Principle

A feature is considered verified only when its implementation has been reviewed and supporting test evidence is available.

A mock demonstration, planned feature or untested integration must not be represented as a verified security capability.
