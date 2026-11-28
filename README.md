# LedgerLock

LedgerLock is a tamper-evident audit-ledger project. The application will create canonical audit records, link them with SHA-256 hashes, retain a trusted signed checkpoint, and report when a stored chain no longer verifies.

This repository contains the demonstration frontend, FastAPI hash-chain API, local and Floci-GCP runtime modes, security architecture documents, CI checks, and project coordination material. The browser starts in an explicitly labelled mock mode. Default live mode uses disposable process memory. When cloud services are explicitly enabled for the local Floci environment, FastAPI uses transactional Firestore storage, KMS checkpoint signing and sanitized Cloud Logging; this is emulator evidence, not real GCP evidence.

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

The default `LEDGERLOCK_API_MODE=mock` enables a browser-only synthetic preview. To exercise the integrated local API, set `LEDGERLOCK_API_MODE=live` before starting Uvicorn. With `USE_CLOUD_SERVICES=false`, restarting the server clears the disposable ledger. The Floci run script enables cloud mode only against `localhost:4588`.

Implemented locally:

- Validated synthetic event creation through `POST /api/events`.
- Ordered in-memory records through `GET /api/ledger`.
- SHA-256 sequence and previous-hash verification through `POST /api/verify`.
- An explicitly labelled local HMAC-SHA256 checkpoint through protected `POST /api/checkpoints` when `LEDGERLOCK_CHECKPOINT_SECRET` and `LEDGERLOCK_ADMIN_TOKEN` are supplied in the process environment.

Still pending and intentionally reported as unavailable in the public Render deployment:

- Persistent Firestore storage.
- Cloud KMS checkpoint signing and verification. The local HMAC checkpoint is not cloud-integration evidence.
- Cloud Run, IAM and Cloud Logging evidence.

## Run the local Floci-GCP verification

Floci-GCP is a local, credential-free emulator. Do not sign in with a personal
Google Cloud account and do not add service-account keys to this repository.

Prerequisites: Docker Desktop running, the repository `.venv` created, and
`requirements-dev.txt` installed. Then run from PowerShell:

```powershell
.\scripts\run_floci_integration.ps1
```

The script starts the isolated emulator on `localhost:4588`, creates a local
EC P-256 signing key, and verifies a synthetic Firestore write/read, Cloud KMS
sign/verify round trip, and redacted Cloud Logging write/read. The opt-in test is
skipped during ordinary unit/CI runs so it cannot accidentally contact a real
cloud service. Stop the emulator without deleting its local volume using:

The same script also starts FastAPI in cloud mode, creates and checkpoints
synthetic records, restarts the API, verifies Firestore persistence and the KMS
checkpoint, and confirms that appending a later record makes the old checkpoint
stale. The public Render deployment keeps cloud services disabled and remains
an in-memory demonstration.

```powershell
docker compose -f docker-compose.floci.yml down
```

Delete the disposable emulator state only when a clean lab reset is intended:

```powershell
docker compose -f docker-compose.floci.yml down -v
```

Before a review or demonstration, run all local checks with:

```powershell
.\scripts\review_preflight.ps1 -IncludeFloci
```

GitHub Actions runs the ordinary regression checks and the isolated Floci
integration as separate jobs. Neither job uses cloud credentials or a billing
account.

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
