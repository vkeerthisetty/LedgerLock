# Logging and Error Handling

## Purpose
Prevent sensitive information from leaking through application errors and security logs.

## Approved log fields
- event_type
- timestamp
- outcome
- correlation_id
- verification_result
- error_category

Only approved, validated values should be logged.

## Prohibited log content
Never log:
- Passwords or authentication tokens
- Private keys or credentials
- Service-account file contents
- Complete sensitive request payloads
- Real student or personal records
- Stack traces in user-facing error responses
- Internal file paths or secret values

## Error handling
The API should return controlled messages for HTTP errors, validation failures, and unexpected exceptions.

Responses must not expose exception details, stack traces, credentials, key material, or internal paths.

## Access
Log access should follow least privilege. Application components may write approved events; only authorised administrators should access security logs.

## Implementation status
The application currently has safe error handlers and a tested security-logging utility. The logging utility is not yet wired into event API routes. Authentication, authorisation, production log access, and cloud IAM controls require separate implementation and verification.

## Evidence
- T06: safe-error handling tests.
- T07: security-logging sanitisation tests.
- Test results must be captured from actual test runs; do not label planned or unimplemented controls as verified.