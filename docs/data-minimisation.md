# Data Minimisation

## Purpose
LedgerLock should process only the information required to create, verify, and review audit records.

## Data handling rules
- Use synthetic actor and resource identifiers during development and demonstrations.
- Collect only fields required by the audit event contract.
- Do not store passwords, access tokens, private keys, credentials, or service-account contents in audit records.
- Do not use real student or personal records in test data.
- Avoid copying complete request payloads into logs or error responses.
- Restrict access to stored records and logs according to the permission matrix.

## Event data
The planned event contract uses:
- event_type
- actor_id
- action
- resource_id
- outcome

The server should generate metadata such as record ID, timestamp, sequence, request ID, and hash information.

## Implementation status
These are design and development requirements. The current application does not yet implement the planned event API or production storage controls. Cloud storage and IAM configuration must be verified separately.