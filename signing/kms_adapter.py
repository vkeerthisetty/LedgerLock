import base64
import hashlib
import hmac
import os


class CheckpointSignerAdapter:
    def __init__(self, use_cloud: bool = False):
        self.use_cloud = use_cloud and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        self.mode = "GCP_CLOUD_KMS" if self.use_cloud else "LOCAL_SIMULATION"
        self._ephemeral_hmac_key = os.urandom(32)
        self.local_key_id = "local-sim://hmac-sha256-ephemeral"

    def _get_kms_key_version_name(self, client) -> str:
        return client.crypto_key_version_path(
            os.getenv("GCP_PROJECT_ID"),
            os.getenv("GCP_REGION", "asia-south1"),
            os.getenv("KMS_KEY_RING", "ledgerlock-keyring"),
            os.getenv("KMS_KEY_NAME", "checkpoint-signer"),
            os.getenv("KMS_KEY_VERSION", "1"),
        )

    def sign_checkpoint(self, payload: str) -> dict:
        payload_bytes = payload.encode("utf-8")
        if self.use_cloud:
            from google.cloud import kms
            client = kms.KeyManagementServiceClient()
            key_name = self._get_kms_key_version_name(client)
            digest = hashlib.sha256(payload_bytes).digest()
            resp = client.asymmetric_sign(request={"name": key_name, "digest": {"sha256": digest}})
            return {
                "mode": self.mode,
                "algorithm": "GCP_KMS_ASYMMETRIC_SIGN",
                "key_id": key_name,
                "signature": base64.b64encode(resp.signature).decode("utf-8"),
            }

        sig = hmac.new(self._ephemeral_hmac_key, payload_bytes, hashlib.sha256).hexdigest()
        return {
            "mode": self.mode,
            "algorithm": "HMAC-SHA256",
            "key_id": self.local_key_id,
            "signature": sig,
        }

    def verify_checkpoint(self, payload: str, signature: str) -> tuple[bool, str]:
        if not signature or not isinstance(signature, str):
            return False, f"Verification FAILED under {self.mode}: empty signature"

        payload_bytes = payload.encode("utf-8")
        if self.use_cloud:
            from google.cloud import kms
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec, padding, utils

            client = kms.KeyManagementServiceClient()
            key_name = self._get_kms_key_version_name(client)
            pub_resp = client.get_public_key(request={"name": key_name})
            public_key = serialization.load_pem_public_key(pub_resp.pem.encode("utf-8"))
            raw_sig = base64.b64decode(signature)
            digest = hashlib.sha256(payload_bytes).digest()

            try:
                if isinstance(public_key, ec.EllipticCurvePublicKey):
                    public_key.verify(raw_sig, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
                else:
                    public_key.verify(
                        raw_sig,
                        digest,
                        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                        utils.Prehashed(hashes.SHA256()),
                    )
                return True, f"Verification PASSED under {self.mode}"
            except Exception as exc:
                return False, f"Verification FAILED under {self.mode}: {type(exc).__name__}"

        expected_sig = hmac.new(self._ephemeral_hmac_key, payload_bytes, hashlib.sha256).hexdigest()
        ok = hmac.compare_digest(expected_sig, signature)
        status = "PASSED" if ok else "FAILED"
        return ok, f"Verification {status} under {self.mode}"
