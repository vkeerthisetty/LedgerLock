# LedgerLock Secret Handling Policy

## 1. Purpose

This document defines how LedgerLock handles secrets and sensitive configuration during development, testing, integration and deployment.

The objective is to prevent accidental exposure of credentials, private keys, access tokens and service-account information.

## 2. Sensitive Information

The following information must be treated as secret:

- API keys and access tokens.
- Passwords and authentication credentials.
- Private signing keys and cryptographic key material.
- Google Cloud service-account credentials.
- Database credentials and connection secrets.
- Session tokens and bearer tokens.

Secret values must never be committed to the Git repository or included in audit-event payloads, application errors or security logs.

## 3. Environment Configuration

- Store local development configuration in an untracked `.env` file when required.
- Use `.env.example` only for safe sample values and configuration names.
- Never place actual passwords, API keys, tokens or private keys in `.env.example`.
- Do not commit local environment files.
- Use environment variables or an approved secret manager for deployment configuration.
- Do not hardcode credentials in Python source files or frontend JavaScript.

## 4. Repository Protection

The project `.gitignore` excludes common sensitive files, including:

- `.env` files, except `.env.example`.
- Private key files (`*.pem`, `*.key`).
- Certificate and key containers (`*.p12`, `*.pfx`).
- Service-account JSON files.
- Application default credential files.

These exclusions reduce accidental commits but do not guarantee that secrets cannot be committed. Files must be inspected before committing and pushing.

If a real credential is accidentally exposed, it must be revoked or rotated immediately. Removing the value from the latest commit alone does not make an exposed credential safe.

## 5. Logging and Error Responses

- Never log secret values, private keys, passwords or access tokens.
- Do not log complete sensitive request payloads.
- Do not return exception details, stack traces, internal paths or credentials to API clients.
- Use approved log fields and controlled error messages.
- Use synthetic identifiers in development and testing.

The current security logger uses an allowlist of fields and rejects suspicious values. Its tests cover approved fields, unapproved fields, suspicious values and non-string values.

## 6. Cryptographic Key Management

LedgerLock plans to use a controlled signing workflow for audit checkpoints.

Private signing keys must not be stored in source code, frontend files, audit records or ordinary application logs.

A production deployment should use an approved key-management service, such as Google Cloud KMS, with restricted IAM permissions and key rotation procedures.

**Current status:** Production KMS integration and actual checkpoint signing are not demonstrated by the current mock implementation.

## 7. Access and Least Privilege

- Only authorised components should access secrets.
- Ordinary test users must not access private keys or signing credentials.
- Administrative access must be restricted and auditable.
- Applications should receive only the credentials and permissions required for their operations.

The permission matrix describes the intended access-control design. Actual authentication and authorization enforcement must be implemented and tested separately.

## 8. Development and Testing Rules

- Use synthetic data and placeholder credentials.
- Never use real student records or personal credentials in test cases.
- Use clearly identifiable dummy values when testing secret exposure.
- Inspect logs, error responses and repository changes for accidental disclosure.
- Do not include real credentials in evidence screenshots or test-output files.

## 9. Implementation Status

| Control | Current status |
|---|---|
| `.env` exclusion | Present in `.gitignore` |
| Private-key file exclusions | Present in `.gitignore` |
| Safe `.env.example` | Uses placeholder configuration |
| Security-log field allowlist | Implemented |
| Suspicious log-value rejection | Implemented |
| Safe unexpected-error response | Implemented |
| Production secret manager | Not demonstrated |
| Production KMS integration | Not demonstrated |
| Authentication and authorization enforcement | Not demonstrated |

## 10. Review

This policy must be reviewed before production deployment and whenever authentication, cloud storage, signing or secret-management integrations are introduced.