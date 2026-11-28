# Project Board Status

## Workflow

Backlog → Ready → In progress → Review → Integration testing → Done

An item is Done only when its code, tests, documentation, evidence and review are complete.

## Current status - 28 November 2026

| Work item | Owner | State | Next action |
|---|---|---|---|
| Architecture, data flow and threat model | Jyoshitha | Review | Update after live cloud integration |
| Hash chain, API and local checkpoint | Syed | Done for local scope | Connect verified cloud interfaces later |
| Floci and live cloud services | Jaanvi | In progress | Verify workspace, services, IAM and operations |
| Safe errors, logging and data handling | Omar | Done for local scope | Review live IAM/logging later |
| Frontend, Render deployment and integration | Keerthi | Done for current scope | Retest after remaining merges |
| T01-T08 local evidence | Keerthi and owners | Done for implemented scope | Repeat after cloud integration |
| Assessment report and demo | Keerthi and team | Review | Timed rehearsal and cloud revision pending |

## Remaining acceptance gates

- Floci workspace and supported-service inventory.
- Firestore durable storage and concurrency test.
- Cloud KMS asymmetric sign/verify test.
- Least-privilege IAM and live logging test.
- FastAPI cloud-mode integration.
- Full regression on the final cloud revision.
- Final five-member demonstration rehearsal.
