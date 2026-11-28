# LedgerLock Demonstration Plan

## Purpose

This runbook provides a reproducible 7-10 minute demonstration using synthetic data. It presents verified local, Render and Floci behavior and labels all remaining limitations accurately.

## Preparation

1. Record the reviewed commit using `git rev-parse HEAD`.
2. Install `requirements-dev.txt` in a clean virtual environment.
3. Run both complete test commands and the repository safety scan.
4. Use only synthetic actors, resources and event descriptions.
5. Hide environment values, browser accounts and unrelated windows.
6. Keep the public Render URL and a tested local fallback ready.

## Local startup

```powershell
$env:LEDGERLOCK_ENV = "development"
$env:LEDGERLOCK_API_MODE = "live"
$env:LEDGERLOCK_CHECKPOINT_SECRET = "review-only-checkpoint-secret-123456789"
$env:LEDGERLOCK_ADMIN_TOKEN = "review-only-admin-token"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

These are disposable local demonstration values. Do not capture the token or secret in screenshots.

## Demonstration timeline

### 0:00-1:00 - Scenario and assets

- Explain that LedgerLock protects the integrity and ordering of synthetic audit history.
- Identify records, hashes, sequences, checkpoints, signing authority, logs and evidence as assets.
- State that the current release is a controlled demonstration, not a production audit system.

### 1:00-2:00 - Architecture and trust boundaries

- Show the architecture and data-flow documents.
- Explain browser-to-API, API-to-ledger, ledger-to-signer and application-to-log boundaries.
- State that the browser never calculates authoritative hashes or accesses signing services directly.

### 2:00-3:30 - Normal workflow

- Open the Render deployment or local live-mode dashboard.
- Confirm `LIVE MODE`.
- Create two synthetic events.
- Show server-generated sequence, timestamp, previous hash and current hash.
- Run verification and show a valid chain.
- Explain that deployed records remain process memory and can reset.

### 3:30-4:30 - Protected local checkpoint

- Open `/docs` on the local application.
- Call `POST /api/checkpoints` using the temporary local administrator token.
- Call `POST /api/verify` and show `checkpoint_valid=true`.
- Explain that this is local HMAC-SHA256, not Cloud KMS.
- Show that an omitted or incorrect token receives HTTP 403.

### 4:30-6:00 - Controlled tampering

Run the controlled tests:

```powershell
python -m unittest tests.test_ledger_core.AuditLedgerTests.test_t02_changed_event_is_detected -v
python -m unittest tests.test_ledger_core.AuditLedgerTests.test_t03_missing_event_is_detected tests.test_ledger_core.AuditLedgerTests.test_t03_reordered_event_is_detected -v
```

- Explain the exact synthetic change.
- Show that the changed, missing and reordered cases fail verification.
- Do not tamper with shared or real records.

### 6:00-7:00 - Safe errors, logging and key handling

- Show T04, T06 and T07 evidence.
- Explain that errors do not return stack traces or submitted secret values.
- Show the sanitized unexpected-error event.
- Run `python scripts/check_repository_safety.py`.

### 7:00-8:15 - Floci-GCP verification

Run or show the saved output from:

```powershell
.\scripts\run_floci_integration.ps1
```

- Show that Firestore, KMS and Logging report `running`.
- Explain the synthetic Firestore write/read, EC P-256 sign/verify and sanitized log write/read.
- State clearly that this is free local Floci-GCP, not a real GCP account and not yet connected to the public website.

### 8:15-9:00 - Regression and deployment

- Show `evidence/test-matrix.md`.
- Report the current local totals: 33 `unittest` tests and 37 `pytest` tests.
- Show the successful GitHub Actions check for the reviewed revision.
- Show the production health endpoint without exposing environment secrets.

### 9:00-9:30 - Claim boundary

- Explain that hash chaining provides tamper evidence, not immutability.
- Explain why process memory is not durable.
- Explain why local HMAC is not Cloud KMS evidence.
- Identify Firestore, KMS and Logging as verified in Floci only; Cloud Run runtime, IAM and active FastAPI cloud wiring remain unverified.

### 9:30-10:00 - Release decision and next steps

- State: controlled demonstration approved with conditions.
- State: complete cloud release not approved.
- Present the named owners and verification gates for the next phase.

## Expected questions

**Why is a hash chain not immutable?**

Hashes expose inconsistent history, but an actor controlling every record and an unprotected chain head can create a new internally consistent history.

**Where is the private key?**

The active local checkpoint uses a shared HMAC secret supplied through the process environment. No private key is committed. The separate Floci KMS adapter holds its EC private key inside the emulator and only exposes sign and public-key operations.

**Does the Render deployment retain records?**

No. The active ledger is process memory and can reset on restart or redeployment.

**Is Firestore or Cloud KMS working?**

Yes, their adapters passed a real protocol round trip against local Floci-GCP. They are not yet connected to the active website and were not tested in a paid or real Google Cloud project.

**Does LedgerLock prove the original event was true?**

No. It protects the integrity of recorded history; it does not prove the truthfulness of the original claim.

## Rehearsal checklist

- [ ] All five members can explain the full data flow.
- [ ] Commands work from a clean environment.
- [ ] Synthetic data is prepared.
- [ ] T01-T08 statuses match the evidence index.
- [ ] No credentials or unrelated windows are visible.
- [ ] Mock, local live and deployed modes are distinguished.
- [ ] Cloud claims match observed evidence.
- [ ] The presentation finishes within 7-10 minutes.
- [ ] A tested local fallback is available.
- [ ] The release recommendation matches the report.
