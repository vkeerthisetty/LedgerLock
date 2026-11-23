# Frontend Acceptance Checklist

The frontend is ready for integration only when all applicable checks pass.

## Core workflow

- [ ] The dashboard loads without a console error.
- [ ] Mock mode is visibly labelled and cannot be mistaken for cloud evidence.
- [ ] The synthetic-event form rejects empty required fields.
- [ ] A successful live submission uses `POST /api/events`.
- [ ] The ledger uses `GET /api/ledger` and displays records in sequence order.
- [ ] Verification uses `POST /api/verify` and clearly distinguishes valid and invalid results.
- [ ] The failing sequence is displayed without exposing unnecessary record data.
- [ ] Loading, empty, success, validation-error, service-error, and tamper-detected states are readable.

## Safety and security

- [ ] The browser never connects directly to Firestore or Cloud KMS.
- [ ] No credentials, private keys, tokens, raw service-account files, or stack traces appear in HTML, JavaScript, logs, screenshots, or API responses.
- [ ] User-provided values are rendered as text, not interpreted as HTML.
- [ ] Controlled tamper actions are available only in explicitly labelled demo mode.
- [ ] Demo tampering affects disposable synthetic data only.

## Usability and evidence

- [ ] Keyboard focus is visible and form fields have labels.
- [ ] The main workflow is usable at mobile width.
- [ ] Status is communicated with text, not colour alone.
- [ ] Evidence screenshots show only the relevant result and contain no secrets.
- [ ] The environment and API mode are recorded with the evidence.
