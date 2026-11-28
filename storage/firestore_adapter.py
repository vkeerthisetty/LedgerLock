"""Local and Firestore storage adapter for LedgerLock."""

import json
import os
from pathlib import Path
from typing import Any


class LedgerStorageAdapter:
    def __init__(
        self,
        use_cloud: bool = False,
        local_path: str = "data/local_ledger.json",
    ):
        self.use_cloud = (
            use_cloud
            and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        )
        self.mode = (
            "GCP_FIRESTORE" if self.use_cloud else "LOCAL_SIMULATION"
        )
        self.local_path = Path(local_path)
        self.checkpoint_path = self.local_path.with_name(
            "local_checkpoint.json"
        )

        if not self.use_cloud:
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.local_path.exists():
                self.local_path.write_text("[]", encoding="utf-8")

        self.collection_name = os.getenv(
            "FIRESTORE_COLLECTION", "audit_ledger"
        )

    def _client(self):
        from google.cloud import firestore
        return firestore.Client()

    def save_record(self, record: dict) -> dict:
        if "PRIVATE KEY" in json.dumps(record).upper():
            raise ValueError(
                "SECURITY_BLOCK: Private key material must never be stored."
            )

        if self.use_cloud:
            db = self._client()
            db.collection(self.collection_name).document(
                str(record["sequence"])
            ).set(record)
        else:
            records = self.read_chain()
            records.append(record)
            records.sort(key=lambda item: item["sequence"])
            self.local_path.write_text(
                json.dumps(records, indent=2), encoding="utf-8"
            )

        return {
            "status": "stored",
            "mode": self.mode,
            "sequence": record.get("sequence"),
        }

    def read_chain(self) -> list[dict]:
        if self.use_cloud:
            db = self._client()
            docs = (
                db.collection(self.collection_name)
                .order_by("sequence")
                .stream()
            )
            return [doc.to_dict() for doc in docs]

        return sorted(
            json.loads(self.local_path.read_text(encoding="utf-8")),
            key=lambda item: item.get("sequence", 0),
        )

    def allocate_sequence(self) -> int:
        """Allocate a unique sequence number in cloud mode."""
        if not self.use_cloud:
            return len(self.read_chain()) + 1

        from google.cloud import firestore

        db = self._client()
        counter_ref = db.collection("_ledger_metadata").document(
            "sequence_counter"
        )

        transaction = db.transaction()

        @firestore.transactional
        def update_counter(transaction):
            snapshot = counter_ref.get(transaction=transaction)

            current = (
                snapshot.get("value")
                if snapshot.exists
                else 0
            )
            next_value = current + 1

            transaction.set(counter_ref, {"value": next_value})
            return next_value

        return update_counter(transaction)

    def save_checkpoint(self, checkpoint: dict) -> None:
        if self.use_cloud:
            db = self._client()
            db.collection("_ledger_metadata").document(
                "checkpoint"
            ).set(checkpoint)
        else:
            self.checkpoint_path.write_text(
                json.dumps(checkpoint, indent=2),
                encoding="utf-8",
            )

    def get_checkpoint(self) -> dict[str, Any] | None:
        if self.use_cloud:
            db = self._client()
            snapshot = db.collection("_ledger_metadata").document(
                "checkpoint"
            ).get()
            return snapshot.to_dict() if snapshot.exists else None

        if not self.checkpoint_path.exists():
            return None

        return json.loads(
            self.checkpoint_path.read_text(encoding="utf-8")
        )
