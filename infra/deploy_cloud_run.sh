#!/usr/bin/env bash
set -euo pipefail

# Least-Privilege IAM & Authenticated Cloud Run Deployment (Jaanvi - Cloud Security Engineer)
if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
  echo "ERROR: GCP_PROJECT_ID must be set (e.g., export GCP_PROJECT_ID=your-gcp-project)." >&2
  exit 1
fi

if [[ "${GCP_PROJECT_ID}" == "floci-local" ]]; then
  echo "ERROR: floci-local is a local emulator project ID. Set a live GCP_PROJECT_ID for Cloud Run deployment." >&2
  exit 1
fi

REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-ledgerlock-api}"
SA_NAME="${SERVICE_ACCOUNT_NAME:-ledgerlock-sa}"
SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

echo "[1/3] Creating dedicated least-privilege runtime service account: ${SA_EMAIL}"
gcloud iam service-accounts create "${SA_NAME}" \
  --project="${GCP_PROJECT_ID}" \
  --display-name="LedgerLock Runtime Service Account" || true

echo "[2/3] Binding least-privilege IAM roles (Firestore, Cloud KMS Signer/Verifier, Cloud Logging Writer)"
for ROLE in "roles/datastore.user" "roles/cloudkms.signerVerifier" "roles/logging.logWriter"; do
  gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}"
done

echo "[3/3] Deploying Cloud Run service with IAM authentication enforced (--no-allow-unauthenticated)"
gcloud run deploy "${SERVICE_NAME}" \
  --project="${GCP_PROJECT_ID}" \
  --source . \
  --region "${REGION}" \
  --service-account "${SA_EMAIL}" \
  --set-env-vars "USE_CLOUD_SERVICES=true,GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_REGION=${REGION}" \
  --no-allow-unauthenticated
