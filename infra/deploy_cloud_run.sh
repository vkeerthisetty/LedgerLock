#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
  echo "ERROR: GCP_PROJECT_ID environment variable must be set (e.g., export GCP_PROJECT_ID=my-gcp-project)." >&2
  exit 1
fi

if [[ "${GCP_PROJECT_ID}" == "floci-local" || "${GCP_PROJECT_ID}" == "replace-with-assigned-project-id" ]]; then
  echo "ERROR: Refusing to deploy to placeholder/local project '${GCP_PROJECT_ID}'. Set a real GCP_PROJECT_ID." >&2
  exit 1
fi

REGION="${GCP_REGION:-asia-south1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-ledgerlock-api}"
FIRESTORE_COLLECTION_NAME="${FIRESTORE_COLLECTION:-audit_ledger}"
KMS_RING="${KMS_KEY_RING:-ledgerlock-keyring}"
KMS_KEY="${KMS_KEY_NAME:-checkpoint-signer}"
KMS_VERSION="${KMS_KEY_VERSION:-1}"
LOG_NAME="${CLOUD_LOG_NAME:-ledgerlock-audit-events}"
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
  --no-allow-unauthenticated \
  --set-env-vars "USE_CLOUD_SERVICES=true,GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_REGION=${REGION},FIRESTORE_COLLECTION=${FIRESTORE_COLLECTION_NAME},KMS_KEY_RING=${KMS_RING},KMS_KEY_NAME=${KMS_KEY},KMS_KEY_VERSION=${KMS_VERSION},CLOUD_LOG_NAME=${LOG_NAME}"
