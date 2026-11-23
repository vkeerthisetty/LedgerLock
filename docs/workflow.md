# Branch and Review Workflow

## Branches

- `docs/security-architecture` — Jyoshitha
- `feat/cloud-integration` — Jaanvi
- `feat/ledger-core` — Syed
- `feat/access-logging` — Omar
- `feat/frontend-evidence-report` — Keerthi

Create short-lived task branches from the owner's primary branch when a change is large enough to review independently.

## Pull requests

Every change must use a pull request. The author must provide:

- What changed and why
- Affected interface or risk
- Tests run and observed results
- Evidence created
- Limitations or unresolved issues
- Reviewer who is not the author

Do not push directly to `main`. Require passing CI and at least one approval before merge. Resolve conflicts on the feature branch and rerun affected tests.

## Integration ownership

Keerthi tracks readiness and coordinates integration. This does not transfer specialist ownership: the backend, cloud, architecture, and access owners must fix defects in their own modules and provide the required evidence.
