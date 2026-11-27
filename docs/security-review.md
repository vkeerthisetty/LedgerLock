# LedgerLock - Identity and Data Security Review

**Role:** Identity and Data Security Engineer
**Project:** LedgerLock - Building a Tamper-Evident Audit Trail
**Review date:** 27 November 2026
**Branch:** `feat/omar-security`

## 1. Access Control

LedgerLock follows the principle of least privilege. The permission matrix defines the intended permissions for four roles:

- Test User
- LedgerLock API
- Verification Tool
- Administrator

Ordinary users must not directly modify audit records, access private signing keys or read internal security logs.

Administrative operations and signing workflows must be restricted and auditable.

The current permission matrix represents the intended security design. Production authentication, role-based authorization and cloud IAM enforcement have not yet been demonstrated.

**Documentation:** `docs/permission-matrix.md`

## 2. Data Handling and Minimisation

LedgerLock should collect and process only the information required to create, verify and review audit records.

The current event API accepts:

- `event_type`
- `actor_id`
- `action`
- `resource_id`
- `outcome`

Server-side validation restricts event types, field lengths and unexpected additional fields.

Development and demonstration environments should use synthetic identifiers rather than real student or personal records.

Passwords, credentials, access tokens and private keys must never be stored in audit records or copied into error responses and logs.

Production retention periods, deletion procedures and cloud access controls still require definition and verification.

**Documentation:** `docs/data-minimisation.md`

## 3. Secret Handling

Secret-handling rules prohibit storing credentials, API keys, private signing keys and service-account contents in source code, audit records or frontend JavaScript.

Repository protections include:

- `.env` exclusions.
- Private-key file exclusions such as `.pem` and `.key`.
- Certificate and key-container exclusions.
- Service-account JSON exclusions.
- A safe `.env.example` containing placeholder configuration.

These protections reduce accidental exposure but do not guarantee that secrets cannot be committed.

Any exposed real credential must be revoked or rotated.

Production secret-manager integration and Google Cloud KMS key protection remain future implementation and verification requirements.

**Documentation:** `docs/secret-handling.md`

## 4. Logging and Redaction

LedgerLock includes a security-logging utility in `app/security_logging.py`.

The utility:
- Uses an allowlist of approved fields.
- Rejects unapproved fields.
- Rejects non-string values.
- Rejects values containing suspicious secret-related terms.
- Adds a UTC timestamp to security events.

The approved fields include event type, outcome, correlation ID, verification result and error category.

The unexpected-error handler uses the security logger to record a controlled application-error event.

The logger is not yet demonstrated across every API operation. Production log access restrictions and cloud logging permissions require further implementation.

### T07 Test Evidence

Four security-logging tests passed:

1. Approved fields are preserved.
2. Unapproved fields are removed.
3. Suspicious free-form values are rejected.
4. Non-string values are rejected.

**Result:** 4/4 tests passed.

**Evidence:** `evidence/T07/test-output.txt`

## 5. Error Handling

The FastAPI application includes controlled handlers for:

- HTTP errors.
- Request validation errors.
- Unexpected application exceptions.

Unexpected exceptions return a generic internal-error response rather than exposing exception details or stack traces.

Validation responses identify relevant fields without returning submitted sensitive values.

### T06 Test Evidence

Five application tests passed, including:

- Dashboard and health response checks.
- Safe HTTP error handling.
- Unexpected-error handling.
- Validation-error handling without exposing submitted values.

**Result:** 5/5 tests passed.

**Evidence:** `evidence/T06/test-output.txt`

## 6. Overall Testing Results

| Test area | Result |
|---|---:|
| T06 - Safe error handling | 5/5 passed |
| T07 - Log sanitisation | 4/4 passed |
| Full project test suite | 24/24 passed |

The tests were executed locally using Python's unittest framework.

The test environment produced a Starlette deprecation warning concerning the use of `httpx` with `TestClient`. It did not prevent the tests from passing.

## 7. Outstanding Security Limitations

The following controls must be addressed before production deployment:

1. Authentication and role-based authorization enforcement.
2. Cloud IAM configuration and access-policy verification.
3. Production secret-manager integration.
4. Google Cloud KMS integration and checkpoint signing.
5. Persistent production storage and access controls.
6. Defined audit-data retention and deletion procedures.
7. Broader security logging coverage across API operations.
8. Production log access restrictions and monitoring.

The current application is a development/mock foundation. Passing local tests does not establish production security or cloud integration.

## 8. Conclusion

The Identity and Data Security work establishes a documented least-privilege permission model, data-minimisation requirements, secret-handling rules, safe error responses and security-log sanitisation.

T06 and T07 passed their targeted local test suites, and the full project test suite passed all 24 tests.

The remaining production security controls have been identified and documented for future implementation and verification.
