# LedgerLock – Data Flow

## 1. Purpose

This document describes the movement of audit-event data through LedgerLock and distinguishes the current local implementation from the intended cloud architecture.

LedgerLock is designed to create a tamper-evident audit trail using canonical records, SHA-256 hashing, hash chaining and independently protected signed checkpoints.

This document explicitly distinguishes implemented functionality, available but unwired adapters, planned integrations and unverified deployment capabilities.

## 2. System Components

The intended system consists of:

1. Frontend – accepts user input and displays ledger information.
2. Backend API – validates requests and controls access to system operations.
3. Record Processor – creates canonical audit records.
4. Hashing Component – calculates SHA-256 hashes and links records.
5. Storage Adapter – stores and retrieves audit records.
6. Checkpoint Component – maintains trusted checkpoint information.
7. Signing Service – signs checkpoints using a protected signing key.
8. Verification Component – checks record and checkpoint integrity.
9. Security Logger – records relevant security events without exposing secrets.

The current API includes an in-memory ledger and local HMAC checkpoint implementation. Firestore, Cloud KMS and Cloud Logging adapters exist in the repository but have not been verified as integrated into the FastAPI runtime.

The complete cloud architecture remains a target design.

## 3. Deployment and Environment Boundaries

### 3.1 Local Development

The repository supports local execution using:

`uvicorn app.main:app --reload`

The application defaults to:

`LEDGERLOCK_API_MODE=mock`

The dashboard uses the API mode setting to select its frontend behaviour.

Two distinct behaviours must be understood:

- Browser mock mode uses disposable browser-side synthetic data and hashing.
- API-backed mode communicates with FastAPI endpoints.

The FastAPI application currently creates an in-memory `AuditLedger`. It does not use Firestore for its active ledger storage.

The API-backed routes include:

- `GET /api/health`
- `POST /api/events`
- `GET /api/ledger`
- `POST /api/verify`
- `POST /api/checkpoints`

The checkpoint endpoint currently uses local HMAC-SHA256 rather than Cloud KMS.

The `LEDGERLOCK_API_MODE=live` setting selects API-backed frontend behaviour. It does not enable live cloud integrations.

`USE_CLOUD_SERVICES=false` is configured in the supplied Render configuration. The existence of cloud adapters does not establish that they are active.

### 3.2 Floci Verification

Floci is identified in the project integration context as a verification environment or process.

Its exact deployment model, execution mechanism and relationship to Render have not yet been confirmed.

Therefore:

- Floci verification results must be associated with the exact source revision tested.
- Verification evidence must identify the test command, result and environment where available.
- Floci must not automatically be described as the production deployment.
- A successful verification result must not be interpreted as proof of untested cloud integrations.

The Floci workflow requires confirmation from the project integration owner.

### 3.3 Render Deployment

The repository contains a `render.yaml` configuration.

The configuration specifies:

- Python runtime.
- `uvicorn app.main:app` as the start command.
- `/api/health` as the health-check path.
- `LEDGERLOCK_API_MODE=live`.
- `USE_CLOUD_SERVICES=false`.
- A configured deployment branch of `main`.

In this configuration, `live` refers to API-backed frontend behaviour, not live Firestore, Cloud KMS or Cloud Logging integration.

The actual deployed source revision, deployment health and runtime behaviour must be independently verified.

The existence of `render.yaml` does not establish that a particular revision is currently deployed or that cloud services are operational.

### 3.4 Cloud Run Deployment

The repository contains a Cloud Run deployment script.

The script configures a Cloud Run service account and proposes IAM permissions for Firestore, Cloud KMS and Cloud Logging before deployment.

However, the script does not establish complete cloud readiness. Firestore provisioning, KMS key configuration, API enablement, runtime environment configuration and application adapter wiring require further work and verification.

The configured Cloud Run deployment uses `--no-allow-unauthenticated`. The frontend and API authentication design must account for this restriction.

Cloud Run must remain labelled prepared or unverified until a successful deployment and integration evidence are available.

## 4. Audit Event Submission

A user submits an audit event through the frontend.

The intended event fields are:

- `event_type`
- `actor_id`
- `action`
- `resource_id`
- `outcome`

Only synthetic identities and test data are permitted during demonstrations and testing.

The browser communicates with the backend API when API-backed mode is selected. It must never access Firestore or Cloud KMS directly.

Browser mock mode is a separate demonstration path and does not establish backend ledger persistence or cloud integration.

## 5. Backend Validation

The FastAPI backend receives the event and validates the submitted fields.

The current event input model uses constrained event types and outcomes, validates relevant string fields and rejects unexpected extra fields.

The backend generates authoritative metadata, including:

- Record ID
- Timestamp
- Sequence number
- Request ID
- Previous hash
- Current hash

The sequence number and hash are generated by the backend's current in-memory ledger implementation.

Important limitation: the current sequence allocation is process-local. It is not a concurrency-safe distributed sequence allocator for multiple application instances.

Authentication and authorization must be reviewed separately. The existence of an API route or an administrative token check does not establish complete role-based access control across all operations.

## 6. Canonical Record Creation

The backend converts the event into a deterministic representation before hashing.

The current ledger implementation uses canonical JSON serialization with sorted keys and compact separators for hash calculation.

Canonicalization ensures consistent representation of the data being hashed.

The implementation and API contract should remain aligned on:

- Field ordering
- Timestamp format
- Character encoding
- Number representation
- Handling of missing and optional fields

Changes to canonical serialization must be tested because they can affect existing record hashes and verification results.

## 7. Hash Generation and Chaining

The backend calculates a SHA-256 hash for each canonical record.

Each record is linked to the previous record through its previous-hash field.

Conceptually:

`Current Hash = SHA-256(Canonical Record Data Including Previous Hash)`

The first record uses a defined initial previous-hash value.

The current `AuditLedger` implementation verifies sequence ordering, previous-hash relationships and recalculated hashes.

Hash chaining alone does not prevent an attacker with sufficient storage access from rewriting an entire chain and recalculating its hashes.

A separately protected checkpoint is required to provide a trusted reference to a previously established chain state.

## 8. Record Storage

The current FastAPI runtime uses an in-memory `AuditLedger`.

Consequences include:

- Records are lost when the application process restarts.
- The current sequence allocation is process-local.
- Multiple instances do not share a common authoritative sequence allocator.
- The current runtime does not establish durable Firestore persistence.

The repository contains a Firestore storage adapter with a cloud-backed path. However, the adapter has not been wired into the active FastAPI ledger runtime.

The adapter's sequence-based document writes also require concurrency-safe allocation and write-conflict handling before being relied upon in a multi-instance deployment.

The intended cloud implementation uses Google Cloud Firestore.

Firestore integration must remain labelled planned or unverified until runtime wiring, persistence, IAM and concurrency behaviour are independently tested.

## 9. Trusted Checkpoint

A checkpoint records a trusted state of the ledger.

It should identify the checkpointed chain state through information such as:

- Latest sequence number
- Chain-head hash
- Checkpoint metadata
- Signing key version or identifier

The current API checkpoint implementation uses HMAC-SHA256 with a configured local secret.

This local checkpoint mechanism is not Cloud KMS evidence.

The repository also contains a Cloud KMS signing adapter. Its presence does not establish that the FastAPI checkpoint route uses Cloud KMS.

The intended cloud implementation must:

- Restrict checkpoint creation to authorized operations.
- Use Cloud KMS for signing.
- Keep private signing keys non-exportable.
- Retrieve the appropriate public key for verification.
- Protect signing and verification permissions.
- Maintain a verifiable relationship between checkpoint metadata and the stored chain state.

The private signing key must never be exposed to the browser, included in records or committed to the repository.

## 10. Verification Process

The current API supports hash-chain verification using the in-memory ledger.

The intended complete cloud verification process should check:

1. Record sequence integrity.
2. Previous-hash relationships.
3. Recalculated record hashes.
4. The latest chain state against the trusted checkpoint.
5. Checkpoint signature validity using the appropriate verification key.

The current local HMAC checkpoint can be verified when its configured secret is available.

Cloud KMS signature verification has not been established as part of the active FastAPI runtime.

A modified, deleted or reordered record should cause verification to report an integrity failure when the change affects the verified chain or checkpointed state.

The verification process does not prove that an event was truthful when it was originally created.

## 11. Verification Result

The backend returns a verification result to the frontend.

The result communicates:

- Whether hash-chain verification passed.
- Number of records checked.
- Failed sequence number, if applicable.
- Checkpoint verification status.
- A safe explanatory message.

The current API distinguishes hash-chain verification from checkpoint verification.

A successful local HMAC checkpoint verification must not be described as successful Cloud KMS verification.

Sensitive data, private keys, credentials and internal stack traces must not be exposed.

## 12. Trust Boundaries

### 12.1 Browser to Backend

All browser input is untrusted and must be validated by the backend.

The browser must not access Firestore or Cloud KMS directly.

The backend must enforce authentication and authorization before protected operations are performed.

### 12.2 Backend to Storage

Only authorized backend operations should access ledger storage.

The cloud implementation must use appropriately restricted Firestore permissions and concurrency-safe record creation.

### 12.3 Backend to Signing Service

Signing operations must be restricted to authorized backend identities.

Cloud KMS must protect non-exportable private signing keys. The backend must not receive private key material.

### 12.4 Backend to Logging

The current application uses local sanitized Python security logging.

A Cloud Logging adapter exists in the repository, but active integration with the FastAPI runtime has not been verified.

Logs must use allowlisted and sanitized fields. Credentials, private keys, tokens and unnecessary complete event payloads must not be logged.

### 12.5 Deployment Boundaries

Local development, Floci verification, Render deployment and Cloud Run deployment must be treated as separate environments or processes.

Evidence from one environment must not automatically be used to claim functionality in another.

## 13. Implementation Status and Limitations

The repository currently provides a dashboard, browser mock mode and an API-backed FastAPI implementation.

The current FastAPI application includes:

- `GET /api/health`
- `POST /api/events`
- `GET /api/ledger`
- `POST /api/verify`
- `POST /api/checkpoints`

The active ledger implementation uses an in-memory `AuditLedger` and server-generated sequence numbers and SHA-256 hashes.

The checkpoint endpoint uses local HMAC-SHA256.

The repository also contains Firestore, Cloud KMS and Cloud Logging adapters. These adapters are not verified as wired into the FastAPI runtime.

The `LEDGERLOCK_API_MODE` setting selects frontend mock or API-backed behaviour. It does not independently activate cloud integrations.

The Render configuration specifies API-backed frontend behaviour while setting `USE_CLOUD_SERVICES=false`.

Cloud Run deployment configuration exists, but complete cloud provisioning, runtime integration and deployment verification remain outstanding.

Floci remains a separate verification context whose exact workflow must be confirmed.

All implementation and deployment claims must be supported by evidence for the exact source revision and environment being assessed.

## 14. Conclusion

LedgerLock is designed to provide tamper evidence for stored audit records by combining deterministic record creation, server-generated sequence numbers, SHA-256 hash chaining and independently protected signed checkpoints.

The current local API provides an in-memory ledger and local HMAC checkpoint functionality. Firestore persistence, Cloud KMS signing and Cloud Logging integration remain unverified in the active FastAPI runtime.

The browser must never directly access Firestore or Cloud KMS. The backend remains the authoritative control point for validation, record creation, storage access, checkpoint operations and verification.

Only synthetic records are permitted in demonstrations and test evidence.

Deployment and verification claims must always match the evidence collected for the corresponding environment.