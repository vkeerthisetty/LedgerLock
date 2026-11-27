
# LedgerLock – Threat Model

## 1. Purpose

This document identifies potential security threats to LedgerLock, the assets that require protection, possible attackers, trust boundaries and proposed mitigations.

The threat model describes risks to the intended system design. It does not claim that every mitigation has already been implemented.

## 2. System Overview

LedgerLock is designed to maintain a tamper-evident audit trail.

It uses:

- Canonical audit records.
- SHA-256 hashing.
- Hash chaining.
- Trusted signed checkpoints.
- Backend-controlled storage operations.
- Integrity verification.
- Security logging.

The browser communicates with the backend API. It must not directly access protected storage or signing services.

## 3. Assets to Protect

| Asset | Security importance |
|---|---|
| Audit records | Must retain integrity |
| Record sequence | Must preserve ordering |
| Record hashes | Must correctly represent records |
| Checkpoint data | Must be protected against unauthorized changes |
| Private signing key | Must remain confidential |
| Public verification key | Must remain trustworthy |
| Credentials and tokens | Must remain confidential |
| Access permissions | Must prevent unauthorized operations |
| Security logs | Must not expose sensitive information |

## 4. Trust Boundaries

### 4.1 Frontend Boundary

The frontend is outside the trusted backend environment.

All input received from the browser must be considered untrusted.

### 4.2 Backend Boundary

The backend validates requests and controls ledger operations.

It must enforce authorization and prevent unauthorized modifications.

### 4.3 Storage Boundary

The storage service contains audit records and checkpoint information.

Access must be restricted to authorized service identities.

### 4.4 Signing Boundary

The signing service protects the private key used to sign checkpoints.

Only authorized backend operations should be permitted to request signatures.

### 4.5 Logging Boundary

Security logs must be protected against unauthorized access and must not contain secrets or unnecessary personal information.

## 5. Threat Actors

Potential threat actors include:

1. Unauthorized external users.
2. Malicious authenticated users.
3. Users submitting malformed or manipulated input.
4. Attackers who obtain compromised application credentials.
5. Insiders with excessive permissions.
6. Attackers attempting to modify stored audit records.

## 6. Threat Identification and Mitigation

### T1 – Unauthorized Audit Event Submission

Threat:
An attacker submits unauthorized or malformed audit events.

Impact:
False or misleading audit records may be created.

Mitigation:
- Validate all input on the backend.
- Enforce authentication and authorization.
- Restrict allowed event types and field lengths.
- Reject invalid requests safely.

### T2 – Audit Record Modification

Threat:
An attacker modifies a previously stored audit record.

Impact:
The integrity of the audit trail may be compromised.

Mitigation:
- Recalculate record hashes during verification.
- Check previous-hash relationships.
- Compare the chain state with a trusted checkpoint.

### T3 – Record Deletion or Reordering

Threat:
An attacker deletes or reorders records.

Impact:
Sequence gaps or broken hash relationships may occur.

Mitigation:
- Assign server-controlled sequence numbers.
- Verify sequence continuity.
- Verify previous-hash relationships.
- Compare the chain against a trusted checkpoint.

### T4 – Checkpoint Manipulation

Threat:
An attacker modifies or replaces checkpoint information.

Impact:
The system may lose its independent reference for verifying the ledger.

Mitigation:
- Sign checkpoints using a protected signing key.
- Verify checkpoint signatures.
- Restrict checkpoint creation and modification.
- Protect checkpoint storage and signing permissions independently.

### T5 – Private Key Exposure

Threat:
A private signing key is exposed through source code, logs, frontend assets or unauthorized access.

Impact:
An attacker may create fraudulent checkpoint signatures.

Mitigation:
- Keep private keys in a protected signing service.
- Apply least-privilege IAM permissions.
- Never expose private keys to the browser.
- Never commit credentials or key material.

### T6 – Unauthorized Storage Access

Threat:
An attacker obtains excessive access to the ledger storage service.

Impact:
Audit records or checkpoint data may be read or modified without authorization.

Mitigation:
- Apply least-privilege access.
- Use dedicated service identities.
- Restrict storage permissions.
- Review access logs.

### T7 – Sensitive Information Exposure

Threat:
Sensitive information is exposed through error messages, logs or API responses.

Impact:
Attackers may obtain credentials, internal system information or unnecessary personal data.

Mitigation:
- Return safe error messages.
- Redact sensitive log fields.
- Never log secrets or private keys.
- Avoid exposing internal stack traces.

### T8 – False Confidence in Mock Mode

Threat:
A user mistakes the frontend mock mode for a working cryptographic or cloud-integrated system.

Impact:
The security capabilities of the project may be incorrectly represented.

Mitigation:
- Clearly label mock mode.
- Distinguish simulated behaviour from verified implementation.
- Require integration evidence before claiming live functionality.

## 7. Important Security Limitations

Hash chaining alone does not make records immutable.

An attacker who can rewrite every record and recompute every hash may construct a different internally consistent chain.

An independently protected signed checkpoint helps detect changes to the checkpointed history.

A compromised event-producing application may also create false events before they are recorded. Hashing cannot prove that the original event was truthful.

Checkpoint frequency and protection of signing keys are important to the overall security design.

## 8. Security Assumptions

The design assumes:

1. Backend validation is correctly implemented.
2. Signing keys are protected.
3. The verification key used to validate signatures is trustworthy.
4. Storage access is appropriately restricted.
5. Checkpoints are protected independently from ordinary ledger modifications.
6. Test evidence uses synthetic data.
7. Cloud configuration and security permissions are reviewed.

These assumptions must be checked during implementation and testing.

## 9. Conclusion

LedgerLock aims to detect unauthorized changes to stored audit records.

Its security depends on the combined use of hash chaining, trusted checkpoints, protected signing operations, backend authorization and reliable verification.

The system must be tested against the identified threats before release.
