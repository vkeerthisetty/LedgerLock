# Environment Setup Instructions (LedgerLock)
**Owner:** Jaanvi (Cloud Security Engineer)

## 1. Prerequisites
- Python 3.10+ (`python --version`)
- Git (`git --version`)
- Google Cloud SDK (`gcloud`, optional for live sandbox deployment)

## 2. Local Setup (No Personal Credentials Required)
1. Clone the repository and switch to your working branch:
   `git clone https://github.com/vkeerthisetty/LedgerLock.git && cd LedgerLock`
2. Copy `.env.example` to `.env` (`.env` is git-ignored and must never be committed).
3. Install dependencies: `pip install -r requirements.txt`
4. Run T04 private-key verification: `python infra/verify_t04.py`

## 3. Live Google Cloud Services (When Sandbox Is Assigned)
1. Run `gcloud auth application-default login` and `gcloud config set project <ASSIGNED_PROJECT_ID>`.
2. Set `USE_CLOUD_SERVICES=true` in `.env`.
3. Run `infra/deploy_cloud_run.sh` to create the least-privilege service account and deploy to Cloud Run.
