# LedgerLock - Security Findings Register

## 1. Purpose

This register records security findings identified during LedgerLock development, testing and review.

Each finding includes its description, severity, evidence, impact, recommended remediation and current status.

## 2. Severity Definitions

| Severity | Meaning |
|---|---|
| Critical | Severe compromise of system security |
| High | Major security weakness with significant impact |
| Medium | Meaningful weakness requiring remediation |
| Low | Limited security impact |
| Informational | Observation or improvement recommendation |

## 3. Findings

### F-001 - Mock Mode Must Not Be Mistaken for Live Verification

- Category: Security communication
- Severity: Informational
- Status: Design consideration
- Description: The frontend foundation starts in explicitly labelled mock mode. Users may incorrectly interpret mock behaviour as evidence of working cryptographic verification or cloud integration.
- Impact: Incorrect security claims and misleading demonstration results.
- Recommendation: Clearly label mock mode and identify which components are implemented, simulated or untested.
- Evidence: Repository README and frontend acceptance documentation.
- Owner: Frontend / Project Coordinator
- Retest required: Yes

### F-002 - Backend Input Validation

- Category: Input validation
- Severity: To be assessed
- Status: Implementation present; further authorization review required
- Description: Browser-submitted event data must be validated by the backend. The current API uses Pydantic validation, restricted event types, field length constraints and rejects extra fields.
- Impact: Malformed or unauthorized input may create invalid or misleading records if validation or authorization controls are insufficient.
- Recommendation: Continue testing server-side validation and implement authentication and authorization before production deployment.
- Evidence: `tests/test_api.py`, including invalid-input and extra-field rejection tests.
- Owner: Backend Engineer
- Retest required: Yes

### F-003 - Checkpoint Signing Key Protection

- Category: Key management
- Severity: To be assessed
- Status: Pending cloud integration review
- Description: The private signing key used for checkpoint signatures must not be exposed to unauthorized users or frontend code.
- Impact: Unauthorized checkpoint signatures could undermine trust in verification.
- Recommendation: Use protected key-management services and least-privilege permissions.
- Evidence: Cloud configuration review and key exposure tests are still required.
- Owner: Cloud Security Engineer
- Retest required: Yes

### F-004 - Audit Chain Integrity Verification

- Category: Data integrity
- Severity: To be assessed
- Status: Pending verification testing
- Description: The system must detect unauthorized record modification, deletion and reordering within the protected verification scope.
- Impact: Undetected changes may undermine audit reliability.
- Recommendation: Verify record hashes, sequence numbers, previous-hash relationships and trusted checkpoints.
- Evidence: Existing T03 verification evidence at `evidence/T03/verification-output.txt`. Additional checkpoint and tampering tests remain necessary.
- Owner: Backend Engineer / Security Architect
- Retest required: Yes

### F-005 - Sensitive Information in Logs and Errors

- Category: Information disclosure
- Severity: To be assessed
- Status: Partially verified; further review required
- Description: API responses and security logs must not expose private keys, credentials, tokens, internal paths or stack traces.
- Impact: Information disclosure may help attackers compromise the system.
- Recommendation:
  - Maintain controlled HTTP, validation and unexpected-error responses.
  - Retain the security-log field allowlist and sanitisation checks.
  - Review logging coverage across API operations.
  - Protect production log access through appropriate authorization and cloud IAM.
- Evidence:
  - T06: `evidence/T06/test-output.txt` - 5 tests passed.
  - T07: `evidence/T07/test-output.txt` - 4 tests passed.
  - Implementation: `app/main.py`, `app/security_logging.py`.
- Owner: Identity and Data Security Engineer
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

T06 and T07 have passed their current targeted local test suites. These results do not establish production security, cloud IAM enforcement, production secret management or complete logging coverage.

Update this document when additional testing produces new evidence.

## 6. Final Review

Reviewed by: Identity and Data Security Engineer
Review date: 27 November 2026
Base project revision: 79ed7be
Outstanding findings: F-002, F-003, F-004 and F-005 require further review or verification.
Release recommendation: Do not treat the current mock implementation as production-ready.