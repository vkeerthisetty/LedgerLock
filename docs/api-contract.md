# LedgerLock API Contract

This contract separates Keerthi's frontend work from Syed's backend implementation. Changes require review from both owners because undocumented response changes will break integration.

All endpoints return JSON. Error responses must be safe for users and must not contain stack traces, credentials, key material, internal file paths, or complete sensitive payloads.

## GET /api/health

Returns service availability without secrets.

```json
{
  "status": "ok",
  "service": "ledgerlock-api",
  "environment": "development"
}
```

## POST /api/events

Creates one synthetic audit event. The server—not the browser—assigns the record ID, timestamp, sequence, request ID, previous hash, and current hash.

Request:

```json
{
  "event_type": "access",
  "actor_id": "actor-demo-01",
  "action": "viewed synthetic record",
  "resource_id": "resource-demo-01",
  "outcome": "success"
}
```

Success response: HTTP `201` with the complete safe audit record.

Validation failure: HTTP `422` with a stable, non-sensitive message and field errors.

## GET /api/ledger

Returns records in ascending sequence order.

```json
{
  "records": [],
  "count": 0,
  "latest_sequence": null,
  "checkpoint": {
    "status": "unavailable",
    "key_version": null
  }
}
```

The browser may display hashes but must never receive private key material, credentials, or unrestricted log payloads.

## POST /api/verify

Runs complete-chain and checkpoint verification.

Valid response:

```json
{
  "valid": true,
  "checked_records": 3,
  "failed_sequence": null,
  "checkpoint_valid": true,
  "message": "Chain and checkpoint verified."
}
```

Invalid response:

```json
{
  "valid": false,
  "checked_records": 2,
  "failed_sequence": 2,
  "checkpoint_valid": false,
  "message": "Integrity verification failed at sequence 2."
}
```

The response identifies the failing sequence without exposing unnecessary record content.

## POST /api/checkpoints

Creates or refreshes a trusted signed checkpoint. This endpoint must be protected and must not be directly exposed to an ordinary demonstration user.

## POST /api/demo/tamper

Optional, disabled by default, and allowed only when `LEDGERLOCK_DEMO_MODE=true`. It must operate on disposable synthetic data and must never provide arbitrary access to production or shared storage.

## Compatibility rules

- Use UTF-8 JSON and ISO 8601 UTC timestamps.
- Keep field names stable and use snake case.
- Never calculate the authoritative hash in the browser.
- Add response fields compatibly; discuss removal or renaming before merge.
- Every API change requires an updated contract, backend test, and frontend integration check.
