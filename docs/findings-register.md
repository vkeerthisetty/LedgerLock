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
- Status: Mitigated in local and Floci cloud modes; live GCP KMS and IAM enforcement open
- Control: Administrator-token requirement, minimum local secret length, protected error responses, and asymmetric `EC_SIGN_P256_SHA256` Cloud KMS signing (`signing/kms_adapter.py`) wired into FastAPI cloud mode (`USE_CLOUD_SERVICES=true`).
- Remaining risk: Public Render and default local mode (`USE_CLOUD_SERVICES=false`) still use a process-held HMAC secret; KMS signing and public-key verification are verified in local Floci-GCP (`evidence/floci/integration-output.txt`), while live GCP KMS and IAM policy enforcement remain untested.

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
- Recommendation: Keep Render's disposable-state warning until the reviewed cloud mode is intentionally deployed; Floci already verifies transactional sequence allocation and API-restart persistence.

### F-007 - Event creation lacks user authentication

- Severity: High
- Status: Open design limitation
- Impact: Any caller able to reach the demonstration API can create a valid synthetic event.
- Existing boundary: Checkpoint creation is protected; demonstration data must remain synthetic.
- Recommendation: Define authenticated roles before any non-demonstration use.

### F-008 - Cloud simulation could be overstated

- Severity: Medium
- Status: Controlled; operationally verified in local Floci only
- Control: Adapter mode labels, disabled-cloud default, Floci runtime evidence and explicit real-GCP limitations.
- Recommendation: Continue distinguishing local Floci evidence from real GCP and public Render behavior.

## Review summary

Reviewed by: Keerthi, Project Coordinator

Review date: 28 November 2026

Controlled demonstration decision: Approved with conditions

Complete cloud decision: Not approved

Outstanding findings: F-003 live KMS scope, F-005 live logging scope, F-006, F-007 and F-008 operational verification.
