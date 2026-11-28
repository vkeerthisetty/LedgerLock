# Project Board Status

## Workflow

Backlog → Ready → In progress → Review → Integration testing → Done

An item is Done only when its code, tests, documentation, evidence and review are complete.

## Current status - 28 November 2026

| Work item | Owner | State | Next action |
|---|---|---|---|
| Architecture, data flow and threat model | Jyoshitha | Review | Align final diagrams with verified Floci scope and active website limitations |
| Hash chain, API and local checkpoint | Syed | Done for local scope | Connect verified Firestore, KMS and Logging adapters to FastAPI |
| Floci-GCP setup and service verification | Keerthi | Done | Firestore, KMS and Logging round trip verified; CI automation added |
| IAM and Cloud Run review | Jaanvi | In progress | Verify IAM enforcement and Cloud Run runtime separately |
| Safe errors, logging and data handling | Omar | Done for local scope | Review live IAM/logging later |
| Frontend, Render deployment and integration | Keerthi | Done for current scope | Run preflight and retest after remaining merges |
| T01-T08 local evidence | Keerthi and owners | Done for implemented scope | Repeat after cloud integration |
| Assessment report and demo | Keerthi and team | Review | Timed rehearsal and final FastAPI-integration revision pending |

## Remaining acceptance gates

- Firestore durable storage and concurrency test.
- Active FastAPI use of the verified Firestore, KMS and Logging adapters.
- Least-privilege IAM enforcement test.
- Cloud Run runtime test if required.
- Full regression on the final cloud revision.
- Final five-member demonstration rehearsal.
