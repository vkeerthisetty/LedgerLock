
# LedgerLock – Security Findings Register

## 1. Purpose

This register records security findings identified during LedgerLock development, testing and review.

Each finding should include its description, severity, evidence, impact, recommended remediation and current status.

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
- Status: Design consideration
- Description: The frontend foundation starts in explicitly labelled mock mode. Users may incorrectly interpret mock behaviour as evidence of working cryptographic verification or cloud integration.
- Impact: Incorrect security claims and misleading demonstration results.
- Recommendation: Clearly label mock mode and identify which components are implemented, simulated or untested.
- Evidence: Repository README and frontend acceptance documentation.
- Owner: Frontend / Project Coordinator
- Retest required: Yes

### F-002 – Backend Input Validation

- Category: Input validation
- Severity: To be assessed
- Status: Pending implementation review
- Description: All browser-submitted event data must be validated by the backend.
- Impact: Malformed or unauthorized input may create invalid or misleading records.
- Recommendation: Enforce server-side validation, field restrictions and authorization.
- Evidence: Backend source review and invalid-input tests.
- Owner: Backend Engineer
- Retest required: Yes

### F-003 – Checkpoint Signing Key Protection

- Category: Key management
- Severity: To be assessed
- Status: Pending cloud integration review
- Description: The private signing key used for checkpoint signatures must not be exposed to unauthorized users or frontend code.
- Impact: Unauthorized checkpoint signatures could undermine trust in verification.
- Recommendation: Use protected key-management services and least-privilege permissions.
- Evidence: Cloud configuration review and key exposure tests.
- Owner: Cloud Security Engineer
- Retest required: Yes

### F-004 – Audit Chain Integrity Verification

- Category: Data integrity
- Severity: To be assessed
- Status: Pending verification testing
- Description: The system must detect unauthorized record modification, deletion and reordering within the protected verification scope.
- Impact: Undetected changes may undermine audit reliability.
- Recommendation: Verify record hashes, sequence numbers, previous-hash relationships and trusted checkpoints.
- Evidence: T01, T02 and T03 test results.
- Owner: Backend Engineer / Security Architect
- Retest required: Yes

### F-005 – Sensitive Information in Logs and Errors

- Category: Information disclosure
- Severity: To be assessed
- Status: Pending review
- Description: API responses and security logs must not expose private keys, credentials, tokens, internal paths or stack traces.
- Impact: Information disclosure may help attackers compromise the system.
- Recommendation: Use safe error responses and redact sensitive log fields.
- Evidence: T06 and T07 test results.
- Owner: Application Security Engineer
- Retest required: Yes

## 4. Findings Status Definitions

- Open: Finding requires investigation or remediation.
- In Progress: Remediation is underway.
- Resolved: A fix has been implemented.
- Retest Required: Fix requires verification.
- Closed: Evidence confirms the issue is addressed.
- Not Applicable: Finding does not apply, with documented justification.

## 5. Review Notes

This register contains design risks and items requiring validation. Entries marked as pending or to be assessed are not confirmed vulnerabilities.

Update this document when actual testing produces new evidence.

## 6. Final Review

Reviewed by:
Review date:
Project revision:
Outstanding findings:
Release recommendation:
