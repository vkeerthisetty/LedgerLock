
import base64
import hashlib
import hmac
import os


class CheckpointSignerAdapter:
    def __init__(self, use_cloud: bool = False):
        self.use_cloud = (
            use_cloud
            and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        )
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

    @staticmethod
    def _kms_client():
        from google.cloud import kms

        endpoint = os.getenv("FLOCI_GCP_ENDPOINT", "").strip()
        if not endpoint:
            return kms.KeyManagementServiceClient()

        import grpc
        from google.cloud.kms_v1.services.key_management_service.transports.grpc import (
            KeyManagementServiceGrpcTransport,
        )

        target = endpoint.removeprefix("http://").removeprefix("https://").rstrip("/")
        transport = KeyManagementServiceGrpcTransport(
            channel=grpc.insecure_channel(target)
        )
        return kms.KeyManagementServiceClient(transport=transport)

    def sign_checkpoint(self, payload: str) -> dict:
        payload_bytes = payload.encode("utf-8")

        if self.use_cloud:
            client = self._kms_client()
            key_name = self._get_kms_key_version_name(client)
            digest = hashlib.sha256(payload_bytes).digest()

            resp = client.asymmetric_sign(
                request={
                    "name": key_name,
                    "digest": {"sha256": digest},
                }
            )

            return {
                "mode": self.mode,
                "algorithm": "GCP_KMS_ASYMMETRIC_SIGN",
                "key_id": key_name,
                "signature": base64.b64encode(resp.signature).decode("utf-8"),
            }

        sig = hmac.new(
            self._ephemeral_hmac_key,
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

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
            try:
                from cryptography.hazmat.primitives import hashes, serialization
                from cryptography.hazmat.primitives.asymmetric import (
                    ec,
                    padding,
                    utils,
                )

                client = self._kms_client()
                key_name = self._get_kms_key_version_name(client)

                pub_resp = client.get_public_key(request={"name": key_name})
                public_key = serialization.load_pem_public_key(
                    pub_resp.pem.encode("utf-8")
                )

                algorithm = getattr(
                    pub_resp.algorithm, "name", str(pub_resp.algorithm)
                )

                raw_sig = base64.b64decode(signature, validate=True)
                digest = hashlib.sha256(payload_bytes).digest()
                prehashed = utils.Prehashed(hashes.SHA256())

                if algorithm.startswith("EC_SIGN_"):
                    if not isinstance(public_key, ec.EllipticCurvePublicKey):
                        return False, "KMS algorithm and public key do not match."

                    public_key.verify(
                        raw_sig,
                        digest,
                        ec.ECDSA(prehashed),
                    )

                elif algorithm.startswith("RSA_SIGN_PSS_"):
                    public_key.verify(
                        raw_sig,
                        digest,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=hashes.SHA256().digest_size,
                        ),
                        prehashed,
                    )

                elif algorithm.startswith("RSA_SIGN_PKCS1_"):
                    public_key.verify(
                        raw_sig,
                        digest,
                        padding.PKCS1v15(),
                        prehashed,
                    )

                else:
                    return False, "Unsupported configured KMS signing algorithm."

                return True, f"Verification PASSED under {self.mode}"

            except Exception as exc:
                return False, (
                    f"Verification FAILED under {self.mode}: "
                    f"{type(exc).__name__}"
                )

        expected_sig = hmac.new(
            self._ephemeral_hmac_key,
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        ok = hmac.compare_digest(expected_sig, signature)
        status = "PASSED" if ok else "FAILED"

        return ok, f"Verification {status} under {self.mode}"
