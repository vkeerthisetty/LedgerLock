
# LedgerLock – Data Flow

## 1. Purpose

This document describes the intended movement of audit-event data through LedgerLock and distinguishes local development, Floci verification and the active Render deployment.

LedgerLock is designed to create a tamper-evident audit trail using canonical records, SHA-256 hashing, hash chaining and independently protected signed checkpoints.

This document distinguishes implemented functionality from planned integrations and unverified deployment capabilities.

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

The complete cloud architecture is a target design. Each component must be verified independently before being described as operational.

## 3. Deployment and Environment Boundaries

### 3.1 Local Development

The repository supports local execution using:

`uvicorn app.main:app --reload`

The current application defaults to:

`LEDGERLOCK_API_MODE=mock`

The current `app/main.py` provides the dashboard and `/api/health` endpoint. Mock mode is a browser-side synthetic preview and is not proof of backend ledger verification or cloud integration.

The `live` setting must only be used when the corresponding backend API implementation is available and verified.

### 3.2 Floci Verification

Floci is identified in the project integration context as a verification environment or process.

Its exact deployment model, execution mechanism and relationship to the active Render deployment have not yet been confirmed.

Therefore:

- Floci verification results must be associated with the exact source revision tested.
- Verification evidence must identify the test command, result and environment where available.
- Floci must not automatically be described as the production deployment.
- A successful verification result must not be interpreted as proof of untested cloud integrations.

The Floci workflow requires confirmation from the project integration owner.

### 3.3 Active Render Deployment

Render is identified by the project team as the active application deployment.

The deployment must be assessed independently from local development and Floci verification.

Deployment evidence should establish:

- The deployed repository revision.
- The configured API mode.
- The available application routes.
- The health endpoint response.
- Whether the deployment uses mock or live backend behaviour.
- Whether any external storage or signing integrations are actually connected.

The existence of an active Render deployment does not establish that Firestore, Cloud KMS or Cloud Logging is operational.

## 4. Audit Event Submission

A user submits an audit event through the frontend.

The intended event fields are:

- event_type
- actor_id
- action
- resource_id
- outcome

Only synthetic identities and test data should be used during demonstrations and testing.

The browser must communicate with the backend API. It must never access Firestore or Cloud KMS directly.

## 5. Backend Validation

The backend receives the event and validates the submitted fields.

It should check that:

- Required fields are present.
- Field values follow the expected format.
- Input lengths and types are within allowed limits.
- Invalid or unexpected input is rejected safely.
- The requester is authorized to perform the requested operation.

The server must assign authoritative metadata, including:

- Record ID
- Timestamp
- Sequence number
- Previous hash
- Current hash

The browser must not be trusted to generate authoritative ledger metadata.

## 6. Canonical Record Creation

After validation, the backend converts the event into a deterministic representation.

Canonicalization ensures that equivalent records are represented consistently before hashing.

The implementation must define:

- Field ordering
- Timestamp format
- Character encoding
- Number representation
- Handling of missing and optional fields

The exact canonicalization rules must be agreed upon by the backend team.

## 7. Hash Generation and Chaining

The backend calculates a SHA-256 hash for each canonical record.

Each record is linked to the previous record through its previous-hash field.

Conceptually:

Current Hash = SHA-256(Canonical Record Data Including Previous Hash)

The first record uses a defined initial previous-hash value.

Changing a record can cause subsequent hash relationships to fail verification.

Hash chaining alone does not prevent an attacker with sufficient storage access from rewriting an entire chain and recalculating its hashes.

## 8. Record Storage

The generated record is passed to the configured storage adapter.

The intended cloud implementation uses Google Cloud Firestore.

A local or mock storage adapter may be used during development.

Records must be retrieved in ascending sequence order.

Storage access must be controlled by backend authorization and appropriate cloud permissions.

Firestore integration must remain labelled planned or unverified until implementation and supporting evidence are reviewed.

## 9. Trusted Checkpoint

A checkpoint records a trusted state of the ledger.

It should include sufficient information to identify the checkpointed chain state, such as:

- Latest sequence number
- Chain-head hash
- Checkpoint metadata
- Signing key version or identifier

The intended cloud implementation uses Google Cloud KMS for signing operations.

Checkpoint creation must require authorization.

Private signing keys must never be exposed to the browser or committed to the repository.

KMS signing and public-key retrieval permissions must be restricted to the required operations.

## 10. Verification Process

The verification component should check:

1. Record sequence integrity.
2. Previous-hash relationships.
3. Recalculated record hashes.
4. The latest chain state against the trusted checkpoint.
5. Checkpoint signature validity.

A modified, deleted or reordered record should cause verification to report an integrity failure when the change affects the verified chain or checkpointed state.

The verification process must not claim to prove that an event was truthful when it was originally created.

## 11. Verification Result

The backend returns a verification result to the frontend.

The result should communicate:

- Whether verification passed.
- Number of records checked.
- Failed sequence number, if applicable.
- Checkpoint verification status.
- A safe explanatory message.

Sensitive data, private keys, credentials and internal stack traces must not be exposed.

## 12. Trust Boundaries

### 12.1 Browser to Backend

All browser input is untrusted and must be validated by the backend.

The browser must not access Firestore or Cloud KMS directly.

### 12.2 Backend to Storage

Only authorized backend operations should access ledger storage.

### 12.3 Backend to Signing Service

Signing operations must be restricted to authorized backend identities.

### 12.4 Backend to Logging

Logs must use allowlisted and sanitized fields. Credentials, private keys, tokens and unnecessary complete event payloads must not be logged.

### 12.5 Deployment Boundaries

Local development, Floci verification and Render deployment must be treated as separate environments or processes.

Evidence from one environment must not automatically be used to claim functionality in another.

## 13. Implementation Status and Limitations

The repository currently provides a frontend foundation with an explicitly labelled mock mode.

The current `app/main.py` provides:

- The dashboard route.
- The `/api/health` endpoint.
- Configuration validation for mock and live API modes.

The API contract describes additional intended routes, but their presence in the contract does not establish that they are implemented.

Persistent cloud storage, signed checkpoint creation, KMS integration and cloud verification require separate implementation and evidence.

Render is identified as the active deployment by the project team. Its actual API mode and cloud connectivity require deployment verification.

Floci is identified as a verification environment or process, but its exact workflow requires confirmation.

## 14. Conclusion

LedgerLock is designed to provide tamper evidence for stored audit records by combining deterministic record creation, SHA-256 hash chaining and independently protected signed checkpoints.

Its security depends on correct implementation, access control, key protection, checkpoint management and verification.

Deployment and verification claims must always match the evidence collected for the corresponding environment.
