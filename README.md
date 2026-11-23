# LedgerLock

LedgerLock is a tamper-evident audit-ledger project. The application will create canonical audit records, link them with SHA-256 hashes, retain a trusted signed checkpoint, and report when a stored chain no longer verifies.

This repository currently contains Keerthi's project foundation: the demonstration frontend, integration contract, GitHub workflow, CI checks, and project coordination documents. The browser starts in an explicitly labelled mock mode so frontend work can be reviewed before the ledger and cloud adapters are merged. Mock mode is not cryptographic or cloud-integration evidence.

## Current responsibility boundaries

- Jyoshitha: architecture, data flow, threats, assumptions, and release criteria.
- Jaanvi: Firestore, Cloud KMS, Cloud Run, Cloud Logging, IAM service configuration, and deployment evidence.
- Syed: backend API, canonical record format, sequence integrity, hash chain, checkpoint interface, and verifier.
- Omar: access control, data minimisation, safe errors, secret handling, and redacted security logging.
- Keerthi: team leadership, frontend, GitHub and CI workflow, integration tracking, regression evidence, report assembly, release coordination, and demonstration.

## Run the frontend foundation

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Copy `.env.example` to `.env` only if local overrides are needed. Do not commit `.env`.
4. Start the application:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000`.

The default `LEDGERLOCK_API_MODE=mock` enables a browser-only synthetic preview. Set `LEDGERLOCK_API_MODE=live` only after the backend implements the contract in [docs/api-contract.md](docs/api-contract.md).

## Tests

Run the repository checks with:

```bash
python -m unittest discover -s tests -v
python -m compileall app tests
```

CI runs these checks for pushes and pull requests. Backend and cloud owners should add their own unit and integration tests without weakening the existing checks.

## Safety rules

- Use synthetic actors, resources, and events only.
- Never commit credentials, private keys, service-account files, raw tokens, or unredacted logs.
- The browser must call the backend API; it must not access Firestore or Cloud KMS directly.
- Controlled tampering is allowed only in labelled demo mode and only against disposable data.
- Label every cloud operation as verified, simulated, or untested based on collected evidence.

## Project documentation

- [API contract](docs/api-contract.md)
- [Frontend acceptance checklist](docs/frontend-acceptance.md)
- [Integration checklist](docs/integration-checklist.md)
- [Project board plan](docs/project-board.md)
- [Branch and review workflow](docs/workflow.md)
