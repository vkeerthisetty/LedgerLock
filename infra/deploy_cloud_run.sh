#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
  echo "ERROR: GCP_PROJECT_ID environment variable must be set (e.g., export GCP_PROJECT_ID=my-gcp-project)." >&2
  exit 1
fi

REGION="${GCP_REGION:-asia-south1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-ledgerlock-api}"
SA_NAME="ledgerlock-sa"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "${SA_NAME}" \
  --project="${GCP_PROJECT_ID}" \
  --display-name="LedgerLock Runtime Service Account" || true

for ROLE in "roles/datastore.user" "roles/cloudkms.signerVerifier" "roles/logging.logWriter"; do
  gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}"
done

gcloud run deploy "${SERVICE_NAME}" \
  --project="${GCP_PROJECT_ID}" \
  --source . \
  --region "${REGION}" \
  --service-account "${SA_EMAIL}" \
  --no-allow-unauthenticated
