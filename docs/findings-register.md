# LedgerLock Security Findings Register

## Severity guidance

| Severity | Meaning in this scenario |
|---|---|
| High | Could permit undetected history changes, unauthorized signing or loss of audit history |
| Medium | Materially weakens a control or exposes unnecessary information |
| Low | Limited weakness with small demonstrated impact |
| Informational | Observation or hardening recommendation without demonstrated vulnerability |

## Findings

### F-001 - Mock behavior could be mistaken for live verification

- Severity: Informational
- Status: Closed for current UI
- Control: Visible mode badges, warnings and documented limitations.
- Evidence: Frontend foundation tests and deployed UI review.

### F-002 - Malformed input could create invalid records

- Severity: Medium
- Status: Closed for implemented schema
- Control: Server-side enumerations, length limits, whitespace handling and rejection of extra fields.
- Evidence: `tests/test_api.py`.

### F-003 - Checkpoint signing authority requires protection

- Severity: High
- Status: Mitigated locally; live KMS open
- Control: Administrator-token requirement, minimum local secret length and protected error responses.
- Remaining risk: the active API still uses a process-held HMAC secret. The KMS adapter is verified only in local Floci-GCP and is not wired into checkpoint creation.

### F-004 - Record modification, removal or reordering

- Severity: High
- Status: Closed for complete available local chain
- Control: Canonical hashing, sequences, previous-hash links and verification.
- Evidence: T01-T03.

### F-005 - Sensitive information in errors or logs

- Severity: Medium
- Status: Closed for tested local scope
- Control: Safe exception handlers, allowlisted fields, restricted values and redaction tests.
- Remaining risk: Live Cloud Logging has not been inspected.

### F-006 - Active ledger is not durable

- Severity: High
- Status: Open
- Impact: Render restart or redeployment can remove audit history and checkpoint state.
- Recommendation: Integrate and verify Firestore with concurrency-safe sequence allocation.

### F-007 - Event creation lacks user authentication

- Severity: High
- Status: Open design limitation
- Impact: Any caller able to reach the demonstration API can create a valid synthetic event.
- Existing boundary: Checkpoint creation is protected; demonstration data must remain synthetic.
- Recommendation: Define authenticated roles before any non-demonstration use.

### F-008 - Cloud simulation could be overstated

- Severity: Medium
- Status: Controlled by documentation; operational verification pending
- Control: Adapter mode labels, disabled-cloud default and explicit report limitations.
- Recommendation: Convert service claims to verified only after Floci/live evidence exists.

## Review summary

Reviewed by: Keerthi, Project Coordinator

Review date: 28 November 2026

Controlled demonstration decision: Approved with conditions

Complete cloud decision: Not approved

Outstanding findings: F-003 live KMS scope, F-005 live logging scope, F-006, F-007 and F-008 operational verification.
