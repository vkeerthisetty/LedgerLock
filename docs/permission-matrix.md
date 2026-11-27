# LedgerLock Permission Matrix

## 1. Purpose

This document defines the intended access permissions for LedgerLock components and user roles. It follows the principle of least privilege, ensuring that each role receives only the permissions required to perform its assigned responsibilities.

These permissions describe the intended security design. They must not be treated as enforced controls until the corresponding authentication and authorization mechanisms are implemented and tested.

## 2. Permission Matrix

| Operation | Test User | LedgerLock API | Verification Tool | Administrator |
|---|---|---|---|---|
| Create audit event | Allowed | Allowed | Denied | Controlled |
| Read ledger | Limited | Allowed | Allowed | Controlled |
| Modify stored records directly | Denied | Controlled workflow | Denied | Controlled |
| Request checkpoint signature | Denied | Allowed | Denied | Controlled |
| Read security logs | Denied | Write only | Limited | Allowed |

## 3. Role Responsibilities

### Test User
- Submit permitted synthetic audit events.
- View only the ledger information exposed through the approved interface.
- Cannot directly modify stored audit records.
- Cannot access private keys or request checkpoint signatures.
- Cannot read internal security logs.

### LedgerLock API
- Validate and process incoming audit-event requests.
- Create records using server-generated metadata.
- Read and update records through controlled application workflows.
- Request checkpoint signing through the approved signing interface.
- Write approved security-log events without unrestricted log-reading access.

### Verification Tool
- Read audit records required for integrity verification.
- Verify sequence numbers, hash links and trusted checkpoints.
- Cannot create or modify audit records.
- Cannot request new checkpoint signatures.
- Receives only the log information required for verification.

### Administrator
- Manage approved administrative operations.
- Access security logs when required for authorised investigation.
- Perform controlled maintenance operations.
- Must not bypass integrity verification or expose private key material.

## 4. Least-Privilege Requirements

- Every role must have only the permissions required for its responsibilities.
- Ordinary users must not access private keys or signing operations.
- Direct modification of stored audit records must be restricted.
- Checkpoint creation and signing must use an authorised workflow.
- Administrative access must be controlled and auditable.
- Permission changes must be reviewed and documented.

## 5. Implementation Status

The permission matrix represents the intended access-control design.

Authentication, role-based authorization and enforcement of these permissions must be implemented and tested before the application can claim that these controls are operational.

## 6. Security Review

The permission model should be reviewed during backend integration and cloud deployment.

Testing must confirm that unauthorised operations are rejected and that authorised operations do not expose unnecessary data or privileges.