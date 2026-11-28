
# LedgerLock – Security Findings Register

## 1. Purpose

This register records security findings identified during LedgerLock development, testing, integration and review.

Each finding includes its description, severity, evidence, impact, recommended remediation, owner and current status.

The register distinguishes confirmed test observations from design risks and items requiring further verification.

## 2. Severity Definitions

| Severity | Meaning |
|---|---|
| Critical | Severe compromise of system security |
| High | Major security weakness with significant impact |
| Medium | Meaningful weakness requiring remediation |
| Low | Limited security impact |
| Informational | Observation or improvement recommendation |

## 3. Findings

### F-001 – Mock Mode Must Not Be Mistaken for Live Verification

- Category: Security communication
- Severity: Informational
- Status: Open – Documentation control required
- Description: The frontend foundation starts in explicitly labelled mock mode. Users may incorrectly interpret mock behaviour as evidence of working cryptographic verification or cloud integration.
- Impact: Incorrect security claims and misleading demonstration results.
- Recommendation: Clearly label mock mode and identify which components are implemented, simulated or untested.
- Evidence: README, frontend acceptance documentation and current application configuration.
- Owner: Frontend / Project Coordinator
- Retest required: Yes

### F-002 – Backend Input Validation and Authorization

- Category: Input validation and access control
- Severity: Medium – Provisional
- Status: In Progress – Validation tests passed; authorization review pending
- Description: Browser-submitted event data must be validated by the backend. Sensitive operations must also require appropriate authorization.
- Impact: Malformed or unauthorized input may create invalid or misleading records.
- Recommendation:
  - Enforce server-side validation.
  - Restrict accepted fields and field lengths.
  - Enforce authorization for protected operations.
  - Reject invalid requests safely.
- Evidence: Automated tests include invalid-input and extra-field rejection checks. Full authorization review requires inspection of the implemented routes and deployment configuration.
- Owner: Backend Engineer / Application Security Engineer
- Retest required: Yes

### F-003 – Checkpoint Signing Key Protection

- Category: Key management
- Severity: High – Provisional
- Status: Open – Cloud integration review pending
- Description: The private signing key used for checkpoint signatures must not be exposed to unauthorized users or frontend code.
- Impact: Unauthorized checkpoint signatures could undermine trust in verification.
- Recommendation:
  - Use protected key-management services.
  - Apply least-privilege permissions.
  - Restrict KMS access to required signing and public-key retrieval operations.
  - Inspect source and deployment configuration for accidental key exposure.
- Evidence: Architecture and API contract documentation describe the intended protected signing design. Operational KMS configuration and key-exposure evidence require confirmation.
- Owner: Cloud Security Engineer
- Retest required: Yes

### F-004 – Audit Chain Integrity Verification

- Category: Data integrity
- Severity: Medium – Provisional
- Status: In Progress – T01 to T03 automated tests passed
- Description: The system must detect unauthorized record modification, deletion and reordering within the protected verification scope.
- Impact: Undetected changes may undermine audit reliability.
- Recommendation:
  - Verify record hashes.
  - Check sequence numbers.
  - Check previous-hash relationships.
  - Compare the chain against a trusted checkpoint when implemented.
- Evidence: Automated tests reported successful results for T01, T02 and T03, including untouched-chain verification, changed-event detection, missing-event detection and reordered-event detection.
- Limitation: Passing hash-chain tests does not establish independent signed checkpoint verification or immutability.
- Owner: Backend Engineer / Security Architect
- Retest required: Yes

### F-005 – Sensitive Information in Logs and Errors

- Category: Information disclosure
- Severity: Medium – Provisional
- Status: In Progress – Application tests passed; complete source and deployment scan requires confirmation
- Description: API responses and security logs must not expose private keys, credentials, tokens, internal paths, exception details or unnecessary complete event payloads.
- Impact: Information disclosure may help attackers compromise the system.
- Recommendation:
  - Use safe error responses.
  - Redact sensitive log fields.
  - Accept only allowlisted logging fields.
  - Avoid logging complete event payloads unnecessarily.
  - Inspect source files, test output and deployment logs.
- Evidence: Automated tests reported successful results for safe unexpected-error responses, validation errors and security logging controls. The complete T06/T07 evidence and cloud logging configuration must be reviewed before closure.
- Owner: Application Security Engineer
- Retest required: Yes

### F-006 – Deployment and Verification Environment Confusion

- Category: Deployment integrity and security communication
- Severity: Informational
- Status: Open – Environment confirmation required
- Description: Floci verification and the active Render deployment represent separate activities. Their exact relationship and configuration must be documented accurately.
- Impact: Verification results may be incorrectly presented as proof of active deployment security, or deployment availability may be mistaken for successful cryptographic verification.
- Recommendation:
  - Record the tested source revision.
  - Record the deployed source revision.
  - Document the Floci verification workflow.
  - Confirm the actual Render API mode.
  - Keep unverified cloud integrations labelled accordingly.
- Evidence: Project integration instructions identify Floci as a verification context and Render as the active deployment. The repository does not yet establish the exact Floci workflow or deployment configuration.
- Owner: Security Architect / Project Coordinator
- Retest required: Yes

### F-007 – Cloud Storage and Logging Permissions

- Category: Cloud access control
- Severity: High – Provisional
- Status: Open – Cloud configuration evidence pending
- Description: Firestore, KMS and Cloud Logging must use restricted identities and least-privilege permissions.
- Impact: Excessive permissions may allow unauthorized access to audit records, signing operations or sensitive log data.
- Recommendation:
  - Restrict Firestore access to required operations.
  - Restrict KMS access to signing and public-key retrieval.
  - Accept only allowlisted and sanitized logging fields.
  - Review service identities and permissions.
- Evidence: Project documentation defines the intended security requirements. Actual cloud configuration must be reviewed by the cloud owner.
- Owner: Cloud Security Engineer
- Retest required: Yes

## 4. Test Execution Summary

The repository test suite was executed using:

`python -m unittest discover -s tests -v`

Recorded result:

- Tests run: 24
- Failures: 0
- Errors: 0
- Overall result: PASS

The run included:

- API validation tests.
- Safe error-handling tests.
- Audit-chain integrity tests.
- Repository security checks.
- Security logging tests.

The test result establishes that the executed automated tests passed for the checked-out source revision. It does not independently establish cloud integration, production configuration or signed checkpoint operation.

## 5. Findings Status Definitions

- Open: Finding requires investigation or remediation.
- In Progress: Remediation or verification is underway.
- Resolved: A fix has been implemented.
- Retest Required: Fix requires verification.
- Closed: Evidence confirms the issue is addressed.
- Not Applicable: Finding does not apply, with documented justification.

## 6. Review Notes

This register contains confirmed test observations and design risks requiring additional verification.

A passing automated test must not be treated as proof of an untested cloud configuration or deployment feature.

Floci verification and Render deployment must be assessed separately.

Findings must only be closed when supporting evidence is available and reviewed.

## 7. Final Review

Reviewed by:

Review date:

Project revision:

Outstanding findings:

Release recommendation:

Approval status:
