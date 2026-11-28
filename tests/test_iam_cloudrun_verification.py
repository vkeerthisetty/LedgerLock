import os
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TestIamAndCloudRunConfiguration(unittest.TestCase):
    """Static configuration checks for IAM least-privilege and Cloud Run hardening.

    NOTE: These tests validate deployment script configuration and documentation only.
    They do NOT prove live GCP IAM enforcement because Floci runs credential-free locally.
    """

    def test_deploy_script_declares_least_privilege_iam_and_cloud_run_auth(self) -> None:
        script_path = REPO_ROOT / "infra" / "deploy_cloud_run.sh"
        content = script_path.read_text(encoding="utf-8")

        self.assertIn("GCP_PROJECT_ID", content)
        self.assertIn("floci-local", content)
        self.assertIn('REGION="${GCP_REGION:-asia-south1}"', content)
        self.assertIn('SA_NAME="ledgerlock-sa"', content)
        self.assertIn("--no-allow-unauthenticated", content)
        self.assertIn("--service-account", content)

        for required_role in (
            "roles/datastore.user",
            "roles/cloudkms.signerVerifier",
            "roles/logging.logWriter",
        ):
            self.assertIn(required_role, content)

        for forbidden_role in (
            "roles/owner",
            "roles/editor",
            "roles/datastore.owner",
            "roles/cloudkms.admin",
        ):
            self.assertNotIn(forbidden_role, content)

        for required_env in (
            "USE_CLOUD_SERVICES=true",
            "GCP_PROJECT_ID=${GCP_PROJECT_ID}",
            "GCP_REGION=${REGION}",
            "FIRESTORE_COLLECTION=",
            "KMS_KEY_RING=",
            "KMS_KEY_NAME=",
            "KMS_KEY_VERSION=",
            "CLOUD_LOG_NAME=",
        ):
            self.assertIn(required_env, content)

    def test_iam_01_evidence_and_docs_preserve_boundary_and_limitations(self) -> None:
        evidence = (REPO_ROOT / "evidence" / "IAM-01" / "iam-cloudrun-verification.txt").read_text(encoding="utf-8")
        self.assertIn("IAM-01", evidence)
        self.assertIn("NOT enforced by Floci", evidence)
        self.assertNotIn("T05_iam_cloudrun_verification", evidence)
        self.assertFalse((REPO_ROOT / "evidence" / "floci-verification" / "T05_iam_cloudrun_verification.txt").exists())

        doc = (REPO_ROOT / "docs" / "cloud-service-verification.md").read_text(encoding="utf-8")
        self.assertIn("## Floci-GCP execution boundary", doc)
        self.assertIn("infra/bootstrap_floci.py", doc)
        self.assertIn("RUN_FLOCI_INTEGRATION=true", doc)
        self.assertIn("evidence/floci/integration-output.txt", doc)
        self.assertIn("## 3. Key-Handling Controls (Test T04)", doc)
        self.assertIn("PRIVATE KEY", doc)

        matrix = (REPO_ROOT / "evidence" / "test-matrix.md").read_text(encoding="utf-8")
        self.assertIn("| IAM-01 |", matrix)

        release = (REPO_ROOT / "docs" / "release-criteria.md").read_text(encoding="utf-8")
        self.assertIn("- [ ] Least-privilege runtime identity is verified", release)

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_GCP_IAM_TEST") == "true",
        "Live GCP IAM enforcement test requires an authorised GCP project (RUN_LIVE_GCP_IAM_TEST=true).",
    )
    def test_live_gcp_iam_policy_enforcement(self) -> None:
        project_id = os.environ["GCP_PROJECT_ID"]
        sa_email = f"ledgerlock-sa@{project_id}.iam.gserviceaccount.com"
        result = subprocess.run(
            [
                "gcloud",
                "projects",
                "get-iam-policy",
                project_id,
                "--flatten=bindings[].members",
                f"--filter=bindings.members:serviceAccount:{sa_email}",
                "--format=value(bindings.role)",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        roles = set(result.stdout.strip().splitlines())
        self.assertEqual(
            roles,
            {
                "roles/datastore.user",
                "roles/cloudkms.signerVerifier",
                "roles/logging.logWriter",
            },
        )


if __name__ == "__main__":
    unittest.main()
