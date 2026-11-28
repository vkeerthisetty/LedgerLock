# LedgerLock

LedgerLock is a tamper-evident audit-ledger project. The application will create canonical audit records, link them with SHA-256 hashes, retain a trusted signed checkpoint, and report when a stored chain no longer verifies.

This repository currently contains the demonstration frontend, an integrated in-memory hash-chain API, security architecture documents, CI checks, and project coordination material. The browser starts in an explicitly labelled mock mode. Mock mode is not cryptographic or cloud-integration evidence. Live mode connects to the local API, but the current in-memory storage is disposable and is not evidence of Firestore, Cloud KMS, Cloud Run, Cloud Logging, or signed-checkpoint integration.

## Current responsibility boundaries

- Jyoshitha: architecture, data flow, threats, assumptions, and release criteria.
- Jaanvi: Firestore, Cloud KMS, Cloud Run, Cloud Logging, IAM service configuration, and deployment evidence.
- Syed: backend API, canonical record format, sequence integrity, hash chain, checkpoint interface, and verifier.
- Omar: access control, data minimisation, safe errors, secret handling, and redacted security logging.
- Keerthi: team leadership, frontend, Floci setup coordination, GitHub and CI workflow, integration tracking, regression evidence, report assembly, release coordination, and demonstration.

## Run the integration baseline

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

The default `LEDGERLOCK_API_MODE=mock` enables a browser-only synthetic preview. To exercise the integrated local API, set `LEDGERLOCK_API_MODE=live` before starting Uvicorn. Live mode currently uses disposable process memory; restarting the server clears the ledger.

Implemented locally:

- Validated synthetic event creation through `POST /api/events`.
- Ordered in-memory records through `GET /api/ledger`.
- SHA-256 sequence and previous-hash verification through `POST /api/verify`.
- An explicitly labelled local HMAC-SHA256 checkpoint through protected `POST /api/checkpoints` when `LEDGERLOCK_CHECKPOINT_SECRET` and `LEDGERLOCK_ADMIN_TOKEN` are supplied in the process environment.

Still pending and intentionally reported as unavailable:

- Persistent Firestore storage.
- Cloud KMS checkpoint signing and verification. The local HMAC checkpoint is not cloud-integration evidence.
- Cloud Run, IAM and Cloud Logging evidence.

## Tests

Run the repository checks with:

```bash
python -m unittest discover -s tests -v
python -m pytest -q
python -m compileall app storage signing logging infra scripts tests
python scripts/check_repository_safety.py
```

CI runs these checks for pushes and pull requests. The committed tests cover the frontend foundation, API validation, T01-T03 integrity cases, local checkpoint, safe errors, logging controls, local adapters and disabled-cloud fallback. Live cloud operations require separate integration evidence.

## Deployment

`render.yaml` defines a Render web service for the verified local API mode. It runs the FastAPI application, checks `/api/health`, generates the local checkpoint secrets in the hosting environment, and keeps cloud services disabled. The deployed in-memory ledger is disposable and may reset whenever the service restarts; it is not Firestore, Cloud KMS, Cloud Run, or Floci evidence.

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
- [Threat model](docs/threat-model.md)
- [Data flow](docs/data-flow.md)
- [Findings register](docs/findings-register.md)
- [Release criteria](docs/release-criteria.md)
- [Security Assessment Report](docs/security-assessment-report.md)
- [Final demonstration plan](docs/demo-plan.md)
- [T01-T08 evidence matrix](evidence/test-matrix.md)
