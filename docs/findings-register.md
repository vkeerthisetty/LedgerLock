# LedgerLock Security Findings Register

## 1. Purpose

This register records security findings identified during LedgerLock development, testing, integration and review.

Each finding includes its description, severity, evidence, impact, recommended remediation, owner and current status.

The register distinguishes confirmed test observations from design risks and items requiring further verification.

## 2. Severity Definitions

| Severity | Meaning |
|---|---|
| High | Could permit undetected history changes, unauthorized signing or loss of audit history |
| Medium | Materially weakens a control or exposes unnecessary information |
| Low | Limited weakness with small demonstrated impact |
| Informational | Observation or hardening recommendation without demonstrated vulnerability |

## 3. Findings

### F-001 - Mock behavior could be mistaken for live verification

- **Category:** Security communication
- **Severity:** Informational
- **Status:** Documentation control implemented; continued review required
- **Description:** The frontend foundation starts in explicitly labelled mock mode. Users may incorrectly interpret mock behaviour as evidence of working cryptographic verification or cloud integration.
- **Impact:** Incorrect security claims and misleading demonstration results.
- **Control:** Visible mode badges, warnings and documented limitations.
- **Recommendation:** Clearly label mock mode and identify which components are implemented, simulated or untested.
- **Evidence:** README, frontend acceptance documentation and current application configuration.
- **Owner:** Frontend / Project Coordinator
- **Retest required:** Yes

### F-002 - Backend Input Validation and Authorization

- **Category:** Input validation and access control
- **Severity:** Medium - Provisional
- **Status:** Validation tests passed; complete authorization review pending
- **Description:** Browser-submitted event data must be validated by the backend. Sensitive operations must also require appropriate authorization.
- **Impact:** Malformed or unauthorized input may create invalid or misleading records.
- **Control:** Server-side enumerations, length limits, whitespace handling and rejection of extra fields, where implemented.
- **Recommendation:**
  - Enforce server-side validation.
  - Restrict accepted fields and field lengths.
  - Enforce authorization for protected operations.
  - Reject invalid requests safely.
- **Evidence:** Automated API validation tests. Full authorization review requires inspection of implemented routes and deployment configuration.
- **Owner:** Backend Engineer / Application Security Engineer
- **Retest required:** Yes

### F-003 - Checkpoint Signing Authority Requires Protection

- **Category:** Key management
- **Severity:** High - Provisional
- **Status:** Local protection implemented; live KMS integration unverified
- **Description:** The private signing key used for checkpoint signatures must not be exposed to unauthorized users or frontend code.
- **Impact:** Unauthorized checkpoint signatures could undermine trust in verification.
- **Control:** Local administrator-token requirement, minimum local secret length and protected error responses, where implemented.
- **Remaining risk:** A process-held local secret is not equivalent to protected cloud key management.
- **Recommendation:**
  - Use protected key-management services.
  - Apply least-privilege permissions.
  - Restrict KMS access to required signing and public-key retrieval operations.
  - Inspect source and deployment configuration for accidental key exposure.
- **Evidence:** Architecture and API contract documentation describe the intended protected signing design. Operational KMS configuration and key-exposure evidence require confirmation.
- **Owner:** Cloud Security Engineer
- **Retest required:** Yes

### F-004 - Record Modification, Removal or Reordering

- **Category:** Data integrity
- **Severity:** High - Provisional
- **Status:** Local chain integrity tests passed; trusted checkpoint verification remains unverified
- **Description:** The system must detect unauthorized record modification, deletion and reordering within the protected verification scope.
- **Impact:** Undetected changes may undermine audit reliability.
- **Control:** Canonical hashing, sequence numbers, previous-hash relationships and verification within the tested local chain.
- **Recommendation:**
  - Verify record hashes.
  - Check sequence numbers.
  - Check previous-hash relationships.
  - Compare the chain against a trusted checkpoint when implemented.
- **Evidence:** T01, T02 and T03 automated tests, including untouched-chain verification, changed-event detection, missing-event detection and reordered-event detection.
- **Limitation:** Passing hash-chain tests does not establish independent signed checkpoint verification or immutability.
- **Owner:** Backend Engineer / Security Architect
- **Retest required:** Yes

### F-005 - Sensitive Information in Errors or Logs

- **Category:** Information disclosure
- **Severity:** Medium - Provisional
- **Status:** Application-level controls tested; live Cloud Logging review pending
- **Description:** API responses and security logs must not expose private keys, credentials, tokens, internal paths, exception details or unnecessary complete event payloads.
- **Impact:** Information disclosure may help attackers compromise the system.
- **Control:** Safe exception handlers, allowlisted fields, restricted values and redaction tests, where implemented.
- **Recommendation:**
  - Use safe error responses.
  - Redact sensitive log fields.
  - Accept only allowlisted logging fields.
  - Avoid logging complete event payloads unnecessarily.
  - Inspect source files, test output and deployment logs.
- **Evidence:** Application-level safe error-handling and logging tests. Complete T06/T07 evidence and cloud logging configuration require review.
- **Owner:** Application Security Engineer
- **Retest required:** Yes

### F-006 - Active Ledger Is Not Durable

- **Category:** Data persistence and availability
- **Severity:** High
- **Status:** Open - Durable storage verification pending
- **Description:** Audit history and checkpoint state require durable storage. An in-memory or otherwise non-persistent deployment may lose data following a restart or redeployment.
- **Impact:** Loss of audit history can undermine the reliability and availability of the ledger.
- **Recommendation:**
  - Integrate durable storage such as the planned Firestore backend.
  - Verify persistence across restarts and redeployments.
  - Implement concurrency-safe sequence allocation.
  - Test recovery and data consistency.
- **Evidence:** Durable cloud storage integration and operational persistence tests have not yet been confirmed.
- **Owner:** Backend Engineer / Cloud Security Engineer
- **Retest required:** Yes

### F-007 - Event Creation Lacks Verified User Authentication

- **Category:** Authentication and access control
- **Severity:** High - Provisional
- **Status:** Open - Authentication review required
- **Description:** The demonstration API must not be treated as a production system with verified user authentication unless the relevant controls are implemented and tested.
- **Impact:** Unauthorized callers may be able to create synthetic events or access operations beyond their intended permissions.
- **Existing boundary:** Checkpoint creation protection must be reviewed separately from ordinary event creation.
- **Recommendation:**
  - Define authenticated user roles.
  - Enforce authorization on protected endpoints.
  - Test unauthorized and insufficiently privileged requests.
  - Keep demonstration data synthetic.
- **Evidence:** Authentication and authorization coverage across the implemented routes requires confirmation.
- **Owner:** Backend Engineer / Application Security Engineer
- **Retest required:** Yes

### F-008 - Cloud Simulation Could Be Overstated

- **Category:** Security communication and deployment integrity
- **Severity:** Medium
- **Status:** Documentation control required; operational verification pending
- **Description:** Simulated adapters, mock mode and planned cloud services could be mistaken for verified production integrations.
- **Impact:** Demonstration results may be presented as proof of cloud security or operational cryptographic verification when they do not establish those claims.
- **Control:** Explicit mode labels and documented implementation limitations.
- **Recommendation:**
  - Clearly distinguish implemented, simulated and planned components.
  - Record the tested source revision.
  - Record the deployed source revision.
  - Document the Floci verification workflow.
  - Confirm the actual Render API mode.
  - Only describe cloud integrations as verified when supporting evidence exists.
- **Evidence:** Project architecture and integration documentation. Exact deployment and cloud configuration require confirmation.
- **Owner:** Security Architect / Project Coordinator
- **Retest required:** Yes

## 4. Test Execution Summary

Recorded automated test runs include:

- An earlier run of 24 tests with zero failures and zero errors.
- A later run of 8 tests with all tests passing.

The recorded tests cover application behavior, validation, error handling, audit-chain integrity and security controls.

Test results establish only that the executed tests passed for their respective checked-out source revisions. They do not independently establish cloud integration, production configuration, durable storage or signed checkpoint operation.

## 5. Findings Status Definitions

- **Open:** Finding requires investigation or remediation.
- **In Progress:** Remediation or verification is underway.
- **Mitigated:** A control reduces the risk, but closure criteria have not been fully established.
- **Resolved:** A fix has been implemented.
- **Retest Required:** Fix requires verification.
- **Closed:** Evidence confirms the issue is addressed within the stated scope.
- **Not Applicable:** Finding does not apply, with documented justification.

## 6. Review Notes

This register contains confirmed test observations and design risks requiring additional verification.

A passing automated test must not be treated as proof of an untested cloud configuration or deployment feature.

Floci verification and Render deployment must be assessed separately.

Findings must only be closed when supporting evidence is available and reviewed.

## 7. Final Review

- **Reviewed by:** Pending confirmation
- **Review date:** Pending confirmation
- **Project revision:** Pending confirmation
- **Outstanding findings:** F-003, F-005, F-006, F-007 and F-008 require further verification.
- **Release recommendation:** Controlled demonstration only, subject to project review and synthetic-data restrictions.
- **Approval status:** Pending team confirmation

## 8. Additional Cloud Architecture Findings

### F-009 - API mode does not activate cloud services

- **Status:** OPEN
- **Evidence:** LEDGERLOCK_API_MODE selects frontend mock/API behaviour. It does not wire cloud adapters into FastAPI.
- **Risk:** A deployment may be mistaken for a live cloud deployment.
- **Action:** Separate frontend mode from cloud-adapter configuration and verify actual service connectivity.

### F-010 - Checkpoint endpoint uses local HMAC

- **Status:** OPEN
- **Evidence:** The active checkpoint implementation uses HMAC-SHA256. The KMS adapter is not wired into the endpoint.
- **Risk:** Local signatures may be misrepresented as KMS-backed signatures.
- **Action:** Integrate KMS signing and public-key verification, then capture key-version and operation evidence.

### F-011 - Ledger storage is currently in memory

- **Status:** OPEN
- **Evidence:** FastAPI initializes an in-memory AuditLedger. The Firestore adapter is not wired into the runtime.
- **Risk:** Records are lost on process restart and are not durably shared across instances.
- **Action:** Integrate Firestore and test persistence and retrieval.

### F-012 - Sequence allocation is not distributed-safe

- **Status:** OPEN
- **Evidence:** Current sequence generation is process-local. The Firestore adapter writes documents by sequence and does not establish atomic allocation.
- **Risk:** Concurrent instances may create duplicate sequences or overwrite records.
- **Action:** Implement transactional sequence allocation and concurrency tests.

### F-013 - Cloud Logging adapter is not active

- **Status:** OPEN
- **Evidence:** The active application uses the local Python security logger. The Cloud Logging adapter is not wired into the runtime.
- **Risk:** Cloud security events may not be delivered or retained.
- **Action:** Integrate Cloud Logging and verify delivery, access controls and sanitization.

### F-014 - Cloud Run provisioning is incomplete or unverified

- **Status:** OPEN
- **Evidence:** The deployment script does not establish complete Firestore and KMS provisioning, key configuration or all required application environment settings.
- **Risk:** Deployment may succeed without a functioning cloud-backed ledger.
- **Action:** Complete provisioning and capture deployment and integration test evidence.

### F-015 - IAM scope requires review

- **Status:** OPEN
- **Evidence:** The deployment script assigns project-level roles. Actual resource-level least-privilege configuration has not been verified.
- **Risk:** A compromised service identity may have broader access than required.
- **Action:** Review and reduce permissions, then retain IAM configuration evidence.

### F-016 - Cloud Run client authentication flow needs validation

- **Status:** OPEN
- **Evidence:** The deployment script uses --no-allow-unauthenticated. The browser/API authentication flow has not been established by this deployment configuration.
- **Risk:** Legitimate browser requests may fail, or an unsafe workaround may expose the API.
- **Action:** Define and test an authenticated client-to-API flow. Keep Firestore and KMS inaccessible directly from the browser.
