@'
# LedgerLock – Deployment Boundaries

## 1. Purpose

This document distinguishes local development, Floci verification, Render deployment and the intended Cloud Run deployment.

Evidence from one environment must not be treated as proof of functionality in another.

## 2. Local Development

- FastAPI runs using Uvicorn.
- The dashboard supports browser mock mode and API-backed mode.
- The API currently uses an in-memory AuditLedger.
- Checkpoints use local HMAC-SHA256.
- Local execution does not establish cloud integration.

## 3. Floci

Floci is a separate verification context.

Its exact deployment configuration and relationship to Render must be confirmed by the integration owner.

Verification evidence must identify the tested source revision, commands and results.

## 4. Render

The repository contains render.yaml.

Its configuration specifies:
- Python runtime.
- FastAPI/Uvicorn startup.
- /api/health health check.
- LEDGERLOCK_API_MODE=live.
- USE_CLOUD_SERVICES=false.
- Deployment branch main.

The live API mode means API-backed frontend behaviour. It does not mean live cloud integration.

The deployed revision and actual health response must be independently verified.

## 5. Cloud Run

The repository contains a Cloud Run deployment script.

The intended deployment uses a dedicated service account and restricted access.

Before claiming cloud readiness, verify:
- Firestore provisioning and persistence.
- Concurrency-safe sequence allocation.
- Cloud KMS key configuration and signing.
- Non-exportability of the KMS private key.
- Cloud Logging delivery.
- Least-privilege IAM permissions.
- API authentication and authorization.
- Frontend access to an authenticated API.

The deployment script alone is not evidence of successful cloud integration.

## 6. Local Fallback Versus Live Cloud

| Capability | Local implementation | Intended cloud implementation |
|---|---|---|
| Ledger storage | In-memory | Firestore |
| Hashing | SHA-256 | SHA-256 |
| Checkpoint signing | Local HMAC-SHA256 | Cloud KMS |
| Verification | Local hash/HMAC | Hash chain and KMS signature |
| Security logging | Local Python logger | Cloud Logging |
| Sequence allocation | Process-local | Concurrency-safe shared allocation |

Local HMAC is a development fallback and is not Cloud KMS evidence.

## 7. Mandatory Security Boundaries

- Browser never contacts Firestore or Cloud KMS directly.
- FastAPI generates authoritative sequences and hashes.
- Cloud KMS private signing keys must be non-exportable.
- Only synthetic records are permitted in testing and demonstrations.
- Credentials and private keys must never be committed to Git.
- Render, Floci and Cloud Run evidence must remain separate.

## 8. Release Evidence

Before production claims are made, record the deployed revision, health-check response, cloud integration test results, IAM configuration and verification evidence.

Unverified capabilities must remain explicitly labelled unverified.
'@ | Set-Content "docs/deployment-boundaries.md" -Encoding UTF8