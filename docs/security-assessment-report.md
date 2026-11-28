# LedgerLock Security Assessment Report

## 1. Executive Summary

LedgerLock is a defensive cybersecurity demonstration that creates synthetic audit records, links them using SHA-256 hashes and detects modification, removal or reordering. The implemented release includes a responsive browser dashboard, a FastAPI backend, server-side validation, authoritative record metadata, hash-chain verification, a protected local HMAC-SHA256 checkpoint, controlled error handling, redacted security logging, local cloud-service adapters and automated regression checks.

The application is deployed at `https://ledgerlock-mt0u.onrender.com/`. On 28 November 2026 the public health endpoint returned `status=ok`, `service=ledgerlock-api` and `environment=production`. A synthetic event was created, retrieved and verified successfully. A checkpoint request without the administrator token returned HTTP 403. The deployed process still stores the active ledger and checkpoint in memory; records can therefore be lost when Render restarts or redeploys the service.

Firestore, live Cloud KMS asymmetric signing, Cloud Run, live Cloud Logging and Floci execution have not been verified. The repository contains adapters, dependencies, configuration guidance and local simulations for these future integrations, but their presence is not operational cloud evidence.

**Release decision:** approved for a controlled local or Render-hosted synthetic demonstration with documented limitations. It is **not approved as a complete durable cloud audit trail** and must not be described as Firestore-, Cloud KMS-, Cloud Run-, Cloud Logging- or Floci-verified until those operations are observed and recorded.

## 2. Scope and Method

This assessment covers the application source at baseline revision `9b195ed` plus documentation and evidence changes on `codex/final-assessment-report`. Testing used Python 3.12.14 on Windows and synthetic actors, resources and event descriptions only.

Assessment activities included:

- Source review of the frontend, API, hash chain, checkpoint, logging and adapter code.
- `unittest` and `pytest` regression suites.
- Python compilation checks.
- T01-T08 control tests and evidence review.
- A tracked-file scan for credential files, private-key markers and high-confidence token patterns.
- Public Render health, event, ledger, verification and authorization smoke tests.
- Review of architecture, data flow, threat assumptions, permissions and release boundaries.

The assessment did not use real student information, production credentials or destructive tests. Source inspection and local simulation do not establish live Firestore, KMS, Cloud Run, Cloud Logging or Floci behavior.

## 3. System Overview

The browser collects synthetic event fields and sends live-mode requests to FastAPI. FastAPI validates field types, lengths, enumerated values and unexpected fields. It assigns the identifier, UTC timestamp, sequence number, request identifier, previous hash and current hash. The browser never calculates authoritative hashes and does not directly access storage or signing services.

The current runtime uses an in-memory `AuditLedger`. Each record hash is calculated from canonical UTF-8 JSON with stable key ordering, excluding the record's own `current_hash`. Verification checks sequential numbering, the previous-hash relationship and the recalculated current hash.

The local checkpoint signs the latest sequence and hash using HMAC-SHA256. Checkpoint creation requires the configured administrator token. This protects the local demonstration against unauthorized checkpoint creation but is not equivalent to asymmetric Cloud KMS signing because the local application holds the shared secret.

The repository also contains disabled-by-default adapters for local JSON persistence, Cloud Firestore, local HMAC signing, Cloud KMS signing and local/cloud security logging. `USE_CLOUD_SERVICES=false` is the verified configuration. Cloud paths remain unverified until tested in the assigned environment.

## 4. Assets and Trust Boundaries

Protected assets include synthetic audit records, record order, record hashes, checkpoint data, signing secrets or key references, administrator authorization data, security logs, evidence files and the verifier implementation.

Important trust boundaries are:

1. **Browser to API:** all browser input is untrusted and requires server-side validation.
2. **API to ledger:** sequence and hash metadata must remain authoritative and server-controlled.
3. **Ledger to checkpoint signer:** ordinary event creation must not gain checkpoint-signing authority.
4. **Application to logs:** only allowlisted and sanitized security fields may cross this boundary.
5. **Application to external services:** cloud claims require verified identity, endpoint, permission and result evidence.
6. **Repository to deployment:** tracked source must not contain secrets; deployment values belong in protected environment settings.

## 5. Findings Summary

| ID | Finding | Severity | Current status | Evidence |
|---|---|---:|---|---|
| F-001 | Mock behavior could be mistaken for live verification | Informational | Closed for current UI | Visible mode labels and README limitations |
| F-002 | Malformed event input could create invalid records | Medium | Closed for implemented schema | API validation and non-echo tests |
| F-003 | Checkpoint signing authority requires protection | High | Mitigated locally; cloud open | Admin-token enforcement and local checkpoint tests |
| F-004 | Record modification, deletion or reordering must be detected | High | Closed for available local chain | T01-T03 |
| F-005 | Errors or logs could expose sensitive information | Medium | Closed for tested local scope | T06-T07 and logging tests |
| F-006 | In-memory ledger and checkpoint are not durable | High | Open | Render restart limitation and source review |
| F-007 | Event creation has no user authentication | High | Open design limitation | Public synthetic demonstration API |
| F-008 | Live cloud operations could be overstated | Medium | Controlled by explicit status labels | Cloud verification document and report limitations |

Severity reflects the proposed audit-ledger scenario. It is not a claim that an external production system was exploited.

## 6. Controls Implemented

### 6.1 Input validation and safe responses

The API restricts event types and outcomes, strips whitespace, enforces length limits and rejects missing or extra fields. Validation responses identify affected fields without echoing submitted values. HTTP and unexpected errors return controlled messages instead of internal paths, stack traces or exception contents.

### 6.2 Hash chaining and sequence integrity

Records receive a server-generated sequence and `previous_hash`. The verifier recalculates every `current_hash`, checks sequence continuity and checks each previous-hash link. T01 verifies an untouched chain. T02 detects changed content. T03 detects removal and reordering.

### 6.3 Local checkpoint protection

The local checkpoint covers schema version, latest sequence, latest hash and key version. HMAC comparison uses constant-time verification. The endpoint rejects missing or incorrect administrator tokens, invalid ledgers and missing signing configuration. The endpoint does not return the shared secret or raw stored checkpoint.

The control is accurately labelled local HMAC-SHA256. It does not prove that Cloud KMS or asymmetric verification works.

### 6.4 Logging and data minimisation

Application security logging uses an allowlist and restricted values. Unexpected errors record an event category and outcome without recording the exception text or request body. The cloud-logging adapter also filters fields and redacts sensitive-looking values in local simulation tests. Live Cloud Logging retention and access controls remain unverified.

### 6.5 Secret handling

`.gitignore`, CI filename checks and `scripts/check_repository_safety.py` reject common environment, service-account and private-key files and scan tracked text for high-confidence markers. The repository uses placeholders in `.env.example`; deployment secrets are generated or supplied through hosting environment settings.

## 7. Tamper Evidence Is Not Immutability

LedgerLock provides tamper evidence within the records and checkpoint supplied to the verifier. It does not make storage immutable. An actor controlling all records, the application and an unprotected checkpoint could replace the entire history. The current Render process can also lose its in-memory history on restart.

The local HMAC checkpoint improves the demonstration by detecting a changed chain head when its secret remains protected. A durable cloud design still requires Firestore persistence, concurrency-safe sequence allocation, independently protected asymmetric KMS signing, least-privilege identities and independently retained logs. Even those controls protect recorded history; they do not prove that the original event description was truthful.

## 8. Test Results

| ID | Test | Result | Scope |
|---|---|---|---|
| T01 | Untouched chain verifies | PASS | Complete available in-memory chain |
| T02 | Changed event is detected | PASS | Controlled disposable copy |
| T03 | Missing or reordered event is detected | PASS | Removal and reversal cases |
| T04 | Records and repository contain no private-key material | PASS | Local records and tracked repository; no live KMS configuration |
| T05 | Report distinguishes tamper evidence from immutability | PASS | Reporting and claim-boundary requirement |
| T06 | Controlled unexpected error is safe and logged | PASS | Local application handler and sanitized event |
| T07 | Source, outputs and local logs inspected for sensitive data | PASS WITH LIMITATIONS | No live Cloud Logging inspection |
| T08 | Complete automated suite is reproducible | PASS FOR IMPLEMENTED SCOPE | 33 `unittest` tests and 37 `pytest` tests passed locally |

Detailed commands, expected results, observations and limitations are indexed in `evidence/test-matrix.md`.

## 9. Deployment Verification

The Render deployment was observed on 28 November 2026:

- `/api/health` returned HTTP 200 and `environment=production`.
- The dashboard displayed `LIVE MODE` and `Evidence coverage T01-T08`.
- A synthetic verification event was created with an authoritative sequence and hash.
- `GET /api/ledger` returned the event in sequence order.
- `POST /api/verify` returned `valid=true` for the available chain.
- `POST /api/checkpoints` without an administrator token returned HTTP 403.
- Browser inspection reported no console errors during the observed verification flow.

The deployed active ledger remains process memory. The smoke test therefore demonstrates a working request flow, not persistence across a restart.

## 10. Limitations

- Render restarts and redeployments clear the active ledger and checkpoint.
- Event creation is intentionally public for the synthetic demonstration and has no user authentication.
- Local HMAC is not asymmetric Cloud KMS signing.
- Firestore code exists but is not connected to the active FastAPI ledger.
- Firestore concurrency and restart persistence are not verified.
- Live Cloud KMS signing and public-key verification are not verified.
- Cloud Run, Cloud Logging, IAM and Floci operations are not verified.
- Local adapter tests do not substitute for service-side authorization evidence.
- A complete team rehearsal and final cloud retest remain future activities.

## 11. Release Recommendation

**Controlled demonstration: approved with conditions.**

The application may be demonstrated locally or on Render using synthetic data, provided the presenter states that storage is disposable and cloud services are unverified. The implementation must not be described as immutable, production-ready or fully cloud-integrated.

**Complete cloud release: not approved.** Approval requires:

1. Verified Floci access and supported-service inventory.
2. Firestore integration with safe sequence allocation and restart-persistence evidence.
3. Cloud KMS asymmetric signing and public-key verification evidence.
4. Least-privilege IAM and checkpoint authorization review.
5. Live Cloud Logging redaction and access evidence.
6. Cloud Run verification if required by the assigned environment.
7. T01-T08 repeated on the final cloud-integrated revision.

## 12. Ownership and Next Steps

- **Jyoshitha:** final architecture, data-flow, threat and release-boundary review.
- **Jaanvi:** Floci inventory; Firestore, KMS, Logging, IAM and Cloud Run service evidence.
- **Syed:** connect the verified storage and signer interfaces to FastAPI and test persistence.
- **Omar:** authorization, data minimisation, error/log review and T04/T06/T07 approval.
- **Keerthi:** coordination, frontend, integration, evidence index, final report and demonstration.

This report must be revised after live cloud integration. Pending work must never be converted to PASS without observed and traceable evidence.
