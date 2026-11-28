# Frontend Acceptance Checklist

The frontend is ready for integration only when all applicable checks pass.

## Core workflow

- [x] The dashboard loads without a console error.
- [x] Mock mode is visibly labelled and cannot be mistaken for cloud evidence.
- [x] The synthetic-event form rejects empty required fields.
- [x] A successful live submission uses `POST /api/events`.
- [x] The ledger uses `GET /api/ledger` and displays records in sequence order.
- [x] Verification uses `POST /api/verify` and clearly distinguishes valid and invalid results.
- [ ] The failing sequence is displayed without exposing unnecessary record data.
- [ ] Loading, empty, success, validation-error, service-error, and tamper-detected states are readable.

## Safety and security

- [x] The browser never connects directly to Firestore or Cloud KMS.
- [x] No credentials, private keys, tokens, raw service-account files, or stack traces were observed in the tested HTML, JavaScript, local logs or API responses.
- [ ] User-provided values are rendered as text, not interpreted as HTML.
- [ ] Controlled tamper actions are available only in explicitly labelled demo mode.
- [ ] Demo tampering affects disposable synthetic data only.

## Usability and evidence

- [x] Keyboard focus is visible and form fields have labels.
- [ ] The main workflow is usable at mobile width.
- [x] Status is communicated with text, not colour alone.
- [ ] Evidence screenshots show only the relevant result and contain no secrets.
- [x] The environment and API mode are recorded with the evidence.

Observed against the local and Render live-mode workflow on 28 November 2026. Unchecked items require a dedicated visual or controlled-tamper acceptance pass before final submission.
