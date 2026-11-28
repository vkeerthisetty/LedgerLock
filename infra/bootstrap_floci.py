"""Create LedgerLock's disposable Floci-GCP KMS resources."""

from __future__ import annotations

import os

import grpc
from google.api_core.exceptions import AlreadyExists
from google.cloud import kms
from google.cloud.kms_v1.services.key_management_service.transports.grpc import (
    KeyManagementServiceGrpcTransport,
)


def kms_client(endpoint: str) -> kms.KeyManagementServiceClient:
    target = endpoint.removeprefix("http://").removeprefix("https://").rstrip("/")
    transport = KeyManagementServiceGrpcTransport(
        channel=grpc.insecure_channel(target)
    )
    return kms.KeyManagementServiceClient(transport=transport)


def main() -> None:
    endpoint = os.getenv("FLOCI_GCP_ENDPOINT", "http://localhost:4588")
    project = os.getenv("GCP_PROJECT_ID", "floci-local")
    region = os.getenv("GCP_REGION", "us-central1")
    ring_id = os.getenv("KMS_KEY_RING", "ledgerlock-keyring")
    key_id = os.getenv("KMS_KEY_NAME", "checkpoint-signer")

    client = kms_client(endpoint)
    location = f"projects/{project}/locations/{region}"
    ring_name = f"{location}/keyRings/{ring_id}"

    try:
        client.create_key_ring(
            request={"parent": location, "key_ring_id": ring_id, "key_ring": {}}
        )
        print(f"created key ring: {ring_name}")
    except AlreadyExists:
        print(f"key ring already exists: {ring_name}")

    try:
        key = client.create_crypto_key(
            request={
                "parent": ring_name,
                "crypto_key_id": key_id,
                "crypto_key": {
                    "purpose": kms.CryptoKey.CryptoKeyPurpose.ASYMMETRIC_SIGN,
                    "version_template": {
                        "algorithm": kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.EC_SIGN_P256_SHA256
                    },
                },
            }
        )
        print(f"created signing key: {key.name}")
    except AlreadyExists:
        print(f"signing key already exists: {ring_name}/cryptoKeys/{key_id}")


if __name__ == "__main__":
    main()
