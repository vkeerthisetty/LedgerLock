# LedgerLock Permission Matrix

## 1. Purpose

This document defines the intended access permissions for LedgerLock components and user roles.

The permission model follows the principle of least privilege: each role should receive only the permissions required to perform its responsibilities.

These permissions describe the intended security design. They must not be treated as enforced controls until authentication and authorization mechanisms are implemented and tested.

## 2. Permission Matrix

| Operation | Test User | LedgerLock API | Verification Tool | Administrator |
|---|---|---|---|---|
| Create audit event | Allowed through API | Allowed | Denied | Controlled |
| Read ledger | Limited | Allowed | Allowed | Controlled |
| Modify stored records directly | Denied | Controlled workflow | Denied | Controlled |
| Request checkpoint signature | Denied | Approved workflow only | Denied | Controlled |
| Write security logs | Denied | Allowed | Limited | Controlled |
| Read security logs | Denied | Not unrestricted | Limited | Allowed |

## 3. Role Responsibilities

### Test User
- Submit permitted synthetic audit events.
- View only ledger information exposed through the approved interface.
- Cannot directly modify stored audit records.
- Cannot access private keys or request checkpoint signatures.
- Cannot read internal security logs.

### LedgerLock API
- Validate and process incoming audit-event requests.
- Create records through the approved ledger workflow.
- Read ledger records through controlled application operations.
- Request checkpoint signing through an approved signing interface when implemented.
- Write approved security-log events.
- Must not expose unrestricted access to logs or cryptographic key material.

### Verification Tool
- Read audit records required for integrity verification.
- Verify sequence numbers, hash links and trusted checkpoints.
- Cannot create or directly modify audit records.
- Cannot request new checkpoint signatures.
- Receives only the log information required for verification.

### Administrator
- Manage approved administrative operations.
- Access security logs when required for authorised investigation.
- Perform controlled maintenance operations.
- Must not bypass integrity verification or expose private key material.
- Administrative actions should be auditable.

## 4. Least-Privilege Requirements

- Every role must have only the permissions required for its responsibilities.
- Ordinary users must not access private keys or signing operations.
- Direct modification of stored audit records must be restricted.
- Checkpoint creation and signing must use an authorised workflow.
- Administrative access must be controlled and auditable.
- Permission changes must be reviewed and documented.
- Access to logs and sensitive configuration must be restricted.

## 5. Implementation Status

The permission matrix represents the intended access-control design.

The current application implements API routes and input validation, but this does not demonstrate production authentication or role-based authorization.

Authentication, authorization, cloud IAM policies and enforcement of the permissions in this matrix must be implemented and tested before the application can claim that these controls are operational.

The current mock implementation must not be treated as proof of production access control.

## 6. Security Review

The permission model should be reviewed during backend integration and cloud deployment.

Testing must confirm that:
- Unauthorised operations are rejected.
- Users cannot access restricted ledger operations.
- Signing operations are restricted to authorised components.
- Log access follows least privilege.
- Administrative actions are controlled and auditable.