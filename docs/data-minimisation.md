# LedgerLock Data Minimisation

## 1. Purpose

LedgerLock should process and retain only the information necessary to create, verify and review audit records.

Data minimisation reduces unnecessary exposure of personal information and sensitive operational data.

## 2. Data Handling Rules

- Use synthetic actor and resource identifiers during development and demonstrations.
- Collect only fields required by the audit-event contract.
- Do not store passwords, access tokens, private keys, credentials or service-account contents in audit records.
- Do not use real student or personal records in test data.
- Avoid copying complete request payloads into logs or error responses.
- Restrict access to stored records and logs according to the permission matrix.
- Do not collect additional personal information unless there is a documented requirement.
- Do not expose sensitive data through frontend responses or debugging output.

## 3. Audit Event Data

The current event API accepts:

- `event_type`
- `actor_id`
- `action`
- `resource_id`
- `outcome`

The API uses server-side validation to restrict permitted event types, field lengths and unexpected fields.

The server-side ledger implementation generates record-related information such as sequence and hash-chain metadata.

Only information necessary for audit creation and integrity verification should be included in records.

## 4. Logging and Error Responses

- Do not log complete event payloads.
- Do not include passwords, tokens, private keys or credentials in logs.
- Use approved security-log fields.
- Do not return submitted sensitive values in validation errors.
- Do not expose exception details or stack traces in API responses.
- Use controlled error messages and synthetic test values.

The current security-logging utility applies an allowlist of approved fields and rejects unapproved or suspicious values.

## 5. Retention and Access

- Retain audit information only according to approved project retention requirements.
- Restrict access to ledger records and security logs.
- Avoid unnecessary copies of audit records and sensitive data.
- Apply least-privilege permissions to components that process or review audit information.

A production retention period, deletion policy and cloud access-control configuration have not yet been demonstrated. These must be defined and verified before production deployment.

## 6. Implementation Status

The current application includes:

- An event creation API with server-side input validation.
- A ledger-reading API.
- A verification API.
- An in-memory ledger implementation.
- A security-logging utility with field filtering.
- Controlled validation and unexpected-error responses.

The current implementation is a development/mock foundation. Production persistence, cloud IAM, authentication, authorization and retention controls require separate implementation and verification.

## 7. Review Requirements

During integration and deployment, verify that:

- Only required event fields are accepted.
- Unexpected fields are rejected.
- Synthetic identifiers are used in test data.
- Sensitive values do not appear in API errors or logs.
- Ledger and log access follows least privilege.
- Retention and deletion requirements are documented and enforced.