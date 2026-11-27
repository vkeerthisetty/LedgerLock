import base64, hashlib, os

class CheckpointSignerAdapter:
    def __init__(self, use_cloud: bool = False):
        self.use_cloud = use_cloud and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        self.mode = "GCP_CLOUD_KMS" if self.use_cloud else "LOCAL_SIMULATION"
        self._ephemeral_secret = hashlib.sha256(os.urandom(32)).hexdigest()

    def sign_checkpoint(self, payload: str) -> dict:
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if self.use_cloud:
            from google.cloud import kms
            client = kms.KeyManagementServiceClient()
            key_name = client.crypto_key_version_path(
                os.getenv("GCP_PROJECT_ID"),
                os.getenv("GCP_REGION", "asia-south1"),
                os.getenv("KMS_KEY_RING", "ledgerlock-keyring"),
                os.getenv("KMS_KEY_NAME", "checkpoint-signer"),
                os.getenv("KMS_KEY_VERSION", "1"),
            )
            resp = client.asymmetric_sign(request={"name": key_name, "digest": {"sha256": bytes.fromhex(digest)}})
            return {"mode": self.mode, "key_id": key_name, "signature": base64.b64encode(resp.signature).decode()}
        sig = hashlib.sha256(f"{self._ephemeral_secret}:{digest}".encode()).hexdigest()
        return {"mode": self.mode, "key_id": "local-sim://ephemeral-rsa2048-public-ref", "signature": sig}

    def verify_checkpoint(self, payload: str, signature: str) -> tuple:
        ok = self.sign_checkpoint(payload)["signature"] == signature
        return ok, f"Verification {'PASSED' if ok else 'FAILED'} under {self.mode}"
