# Least-Privilege IAM & Cloud Run Deployment (Jaanvi - Cloud Security Engineer)
gcloud iam service-accounts create ledgerlock-sa --display-name="LedgerLock Runtime Service Account"
gcloud projects add-iam-policy-binding <PROJECT_ID> --member="serviceAccount:ledgerlock-sa@<PROJECT_ID>.iam.gserviceaccount.com" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding <PROJECT_ID> --member="serviceAccount:ledgerlock-sa@<PROJECT_ID>.iam.gserviceaccount.com" --role="roles/cloudkms.signerVerifier"
gcloud projects add-iam-policy-binding <PROJECT_ID> --member="serviceAccount:ledgerlock-sa@<PROJECT_ID>.iam.gserviceaccount.com" --role="roles/logging.logWriter"
gcloud run deploy ledgerlock-api --source . --region asia-south1 --service-account ledgerlock-sa@<PROJECT_ID>.iam.gserviceaccount.com --allow-unauthenticated
