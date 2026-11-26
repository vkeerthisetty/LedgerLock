
# LedgerLock – Data Flow

## 1. Purpose

This document describes how audit-event data is intended to move through LedgerLock, from submission to storage and integrity verification.

LedgerLock is designed to create a tamper-evident audit trail using canonical records, SHA-256 hashing, hash chaining and trusted signed checkpoints.

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

## 3. Audit Event Submission

A user submits an audit event through the frontend.

The event contains the following fields:

- event_type
- actor_id
- action
- resource_id
- outcome

Only synthetic identities and test data should be used during demonstrations and testing.

The frontend sends the request to the backend API using HTTP.

## 4. Backend Validation

The backend receives the event and validates the submitted fields.

It checks that:

- Required fields are present.
- Field values follow the expected format.
- Input lengths and types are within allowed limits.
- Invalid or unexpected input is rejected safely.

The server is responsible for assigning authoritative metadata, including:

- Record ID
- Timestamp
- Sequence number
- Previous hash
- Current hash

The browser must not be trusted to generate authoritative ledger metadata.

## 5. Canonical Record Creation

After validation, the backend converts the event into a deterministic representation.

Canonicalization ensures that equivalent records are represented consistently before hashing.

The implementation must define:

- Field ordering
- Timestamp format
- Character encoding
- Number representation
- Handling of missing and optional fields

The exact canonicalization rules must be agreed upon by the backend team.

## 6. Hash Generation and Chaining

The backend calculates a SHA-256 hash for each canonical record.

Each record is linked to the previous record through its previous-hash field.

Conceptually:

Current Hash = SHA-256(Canonical Record Data Including Previous Hash)

The first record uses a defined initial previous-hash value.

This creates a chain in which changing an earlier record causes subsequent hash relationships to fail verification.

## 7. Record Storage

The generated record is passed to the configured storage adapter.

The intended cloud implementation uses Google Cloud Firestore.

A local or mock storage adapter may be used during development.

Records must be retrieved in ascending sequence order.

Storage access must be controlled by backend authorization and appropriate cloud permissions.

## 8. Trusted Checkpoint

A checkpoint records a trusted state of the ledger.

It should include sufficient information to identify the checkpointed chain state, such as:

- Latest sequence number
- Chain-head hash
- Checkpoint metadata
- Signing key version or identifier

The exact checkpoint format must be agreed upon by the backend and cloud teams.

The intended cloud implementation uses Google Cloud KMS for signing operations.

Private signing keys must never be exposed to the browser or committed to the repository.

## 9. Verification Process

The verification component checks:

1. Record sequence integrity.
2. Previous-hash relationships.
3. Recalculated record hashes.
4. The latest chain state against the trusted checkpoint.
5. Checkpoint signature validity.

A modified, deleted or reordered record should cause verification to report an integrity failure when that change affects the verified chain or checkpointed state.

The verification process must not claim to prove that an event was truthful when it was originally created.

## 10. Verification Result

The backend returns a verification result to the frontend.

The result should communicate:

- Whether verification passed.
- Number of records checked.
- Failed sequence number, if applicable.
- Checkpoint verification status.
- A safe explanatory message.

Sensitive data, private keys, credentials and internal stack traces must not be exposed.

## 11. Trust Boundaries

The main trust boundaries are:

### 11.1 Frontend to Backend

All browser input is untrusted and must be validated by the backend.

### 11.2 Backend to Storage

Only authorized backend operations should access ledger storage.

### 11.3 Backend to Signing Service

Signing operations must be restricted to authorized backend identities.

### 11.4 Backend to Logging

Logs must avoid credentials, private keys, tokens and unnecessary sensitive information.

## 12. Implementation Status and Limitations

The repository currently provides a frontend foundation with an explicitly labelled mock mode.

Mock mode is intended for reviewing frontend behaviour and is not evidence of cryptographic verification or cloud integration.

The actual implementation of record hashing, persistent storage, checkpoint signing and verification must be confirmed through source-code review, integration tests and recorded evidence.

## 13. Conclusion

LedgerLock is designed to provide tamper evidence for stored audit records by combining deterministic record creation, SHA-256 hash chaining and independently protected signed checkpoints.

Its security depends on correct implementation, access control, key protection, checkpoint management and verification.
