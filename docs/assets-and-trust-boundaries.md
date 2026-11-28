# LedgerLock – Assets and Trust Boundaries

## 1. Purpose

This document identifies the assets that LedgerLock must protect, the system components that handle those assets, and the trust boundaries between them.

It describes the intended cloud architecture and distinguishes target security controls from currently verified implementation.

## 2. System Assets

| Asset | Description | Security requirement |
|---|---|---|
| Audit records | Synthetic event records stored in the ledger | Integrity, availability and controlled access |
| Record sequence | Authoritative ordering of audit records | Uniqueness and consistency |
| Canonical record data | Deterministic representation used for hashing | Consistent serialization |
| Record hashes | SHA-256 hashes linking records | Integrity verification |
| Chain-head hash | Hash identifying the latest ledger state | Integrity and checkpoint consistency |
| Checkpoint metadata | Trusted reference to a ledger state | Integrity and controlled updates |
| Private signing key | Key used to sign checkpoints | Confidentiality and non-exportability |
| Public verification key | Public key used to verify signatures | Authenticity and integrity |
| API credentials | Credentials used to authorize operations | Confidentiality and controlled use |
| Security logs | Sanitized records of security-relevant events | Confidentiality, integrity and availability |
| Deployment configuration | Runtime and cloud-service configuration | Integrity and secret protection |

Only synthetic actors, resources and audit events are permitted in demonstrations and test evidence.

## 3. System Components

1. Browser frontend – submits synthetic events and displays results.
2. FastAPI backend – validates requests and controls access to system operations.
3. Record processor – constructs canonical audit records.
4. Hashing component – calculates SHA-256 hashes and links records.
5. Storage adapter – stores and retrieves audit records.
6. Checkpoint component – maintains trusted checkpoint information.
7. Signing service – signs checkpoints using a protected signing key.
8. Verification component – checks record and checkpoint integrity.
9. Security logger – records relevant security events using sanitized fields.

The complete cloud architecture is a target design. Each component must be independently implemented and verified before it is described as operational.

## 4. Trust Boundaries

### 4.1 Browser to Backend

The browser is an untrusted environment.

Requirements:
- All browser-submitted data must be validated by FastAPI.
- The server generates authoritative record identifiers, timestamps, sequences and hashes.
- The browser must never access Firestore or Cloud KMS directly.
- Authentication and authorization must be enforced by the backend.
- Secrets and private signing material must never be sent to the browser.

### 4.2 Backend to Storage

The backend communicates with the configured storage adapter.

Requirements:
- Storage operations must be restricted to authorized backend identities.
- The cloud implementation must use appropriate Firestore permissions.
- Sequence allocation and record writes must be concurrency-safe.
- Storage responses must be validated before being trusted.
- Direct unauthorized record modification must be restricted.

### 4.3 Backend to Signing Service

The backend requests checkpoint signatures from the signing service.

Requirements:
- Only authorized backend identities may request signing operations.
- The private signing key must remain non-exportable in Cloud KMS.
- The backend must not receive or store private key material.
- Public-key retrieval and signature verification must be supported.
- Signing operations must be auditable.

### 4.4 Backend to Security Logging

The backend sends security-relevant events to the logging component.

Requirements:
- Only allowlisted fields should be logged.
- Credentials, private keys and tokens must never be logged.
- Complete event payloads should not be logged unnecessarily.
- Logging failures must not expose sensitive internal information.
- Cloud Logging access must be restricted.

### 4.5 Deployment Boundaries

Local development, Floci verification, Render deployment and Cloud Run deployment must be treated as separate environments or processes.

Evidence collected in one environment must not automatically establish functionality in another.

## 5. Intended Cloud Service Identities

| Identity | Intended responsibility |
|---|---|
| Browser user | Access approved frontend/API operations |
| FastAPI runtime identity | Perform authorized backend operations |
| Firestore permissions | Read and write permitted ledger documents |
| Cloud KMS permissions | Sign checkpoints and retrieve public keys |
| Cloud Logging permissions | Write sanitized security events |
| Administrator | Perform approved administrative operations |

The intended Cloud Run runtime identity is `ledgerlock-sa`.

The deployment script proposes Firestore, Cloud KMS and Cloud Logging roles. Actual IAM grants, resource-level permissions and runtime identity must be reviewed and verified independently.

## 6. Key Protection Requirements

- Cloud KMS must protect the checkpoint signing private key.
- Private keys must not be exported or embedded in application source code.
- Private keys must not be placed in environment variables.
- Private keys must not be sent to the browser.
- Private keys must not be written to audit records or logs.
- Local HMAC signing is a development fallback and is not evidence of Cloud KMS integration.

## 7. Current Implementation Status

The current API-backed application uses an in-memory ledger and a local HMAC checkpoint implementation.

The Firestore, KMS and Cloud Logging adapters exist in the repository, but their integration with the FastAPI runtime has not been verified.

The permission matrix describes intended access controls. It must not be interpreted as proof that every permission is currently enforced.

## 8. Security Review Requirements

Before cloud release, reviewers must verify:

1. Backend authentication and authorization.
2. Server-controlled sequence allocation.
3. Durable Firestore persistence.
4. Concurrency-safe record creation.
5. Cloud KMS signing and public-key verification.
6. Non-exportability of the configured KMS private key.
7. Sanitized Cloud Logging delivery.
8. Least-privilege service identities.
9. Separation of local, Floci, Render and Cloud Run environments.
10. Use of synthetic records in all demonstration evidence.

## 9. Conclusion

LedgerLock relies on clear trust boundaries between the browser, backend, storage, signing service and logging infrastructure.

The backend is the authoritative control point. Cloud services must be accessed through authorized backend operations, and private signing keys must remain protected within the signing service.

All implementation and deployment claims must match independently reviewed evidence.