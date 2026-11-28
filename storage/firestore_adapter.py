
"""Local and Firestore storage adapter for LedgerLock."""

import json
import os
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ledger_core import GENESIS_HASH, calculate_hash


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

        self.collection_name = os.getenv(
            "FIRESTORE_COLLECTION", "audit_ledger"
        )
        self.metadata_collection_name = (
            f"_{self.collection_name}_metadata"
        )

        if not self.use_cloud:
            self.local_path.parent.mkdir(parents=True, exist_ok=True)

            if not self.local_path.exists():
                self.local_path.write_text("[]", encoding="utf-8")

    def _client(self):
        """Create a Firestore client, supporting the Floci emulator."""

        from google.cloud import firestore

        project_id = (
            os.getenv("GCP_PROJECT_ID")
            or os.getenv("GOOGLE_CLOUD_PROJECT")
        )

        if not project_id:
            raise RuntimeError(
                "GCP_PROJECT_ID is required when cloud services are enabled."
            )

        if os.getenv("FIRESTORE_EMULATOR_HOST"):
            from google.auth.credentials import AnonymousCredentials

            return firestore.Client(
                project=project_id,
                credentials=AnonymousCredentials(),
            )

        return firestore.Client(project=project_id)

    def _check_record(self, record: dict) -> None:
        """Prevent private key material from entering the ledger."""

        if "PRIVATE KEY" in json.dumps(record).upper():
            raise ValueError(
                "SECURITY_BLOCK: Private key material must never be stored."
            )

    def add_event(self, event: dict[str, str]) -> dict[str, Any]:
        """Create and persist a record with a unique sequence number."""

        if not self.use_cloud:
            records = self.read_chain()

            previous_hash = (
                records[-1]["current_hash"]
                if records
                else GENESIS_HASH
            )

            record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z"),
                "sequence": len(records) + 1,
                "request_id": str(uuid.uuid4()),
                **event,
                "previous_hash": previous_hash,
            }

            record["current_hash"] = calculate_hash(record)
            self.save_record(record)

            return record

        from google.cloud import firestore

        db = self._client()
        records_ref = db.collection(self.collection_name)

        metadata_ref = db.collection(self.metadata_collection_name)
        counter_ref = metadata_ref.document("sequence_counter")

        transaction = db.transaction()

        @firestore.transactional
        def create_record(txn):
            counter = counter_ref.get(transaction=txn)
            current = counter.get("value") if counter.exists else 0

            next_sequence = current + 1

            previous_hash = GENESIS_HASH

            if current > 0:
                previous_ref = records_ref.document(str(current))
                previous_snapshot = previous_ref.get(transaction=txn)

                if not previous_snapshot.exists:
                    raise RuntimeError(
                        "Ledger sequence is inconsistent."
                    )

                previous_hash = previous_snapshot.to_dict()["current_hash"]

            record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z"),
                "sequence": next_sequence,
                "request_id": str(uuid.uuid4()),
                **event,
                "previous_hash": previous_hash,
            }

            record["current_hash"] = calculate_hash(record)
            self._check_record(record)

            txn.set(counter_ref, {"value": next_sequence})

            txn.create(
                records_ref.document(str(next_sequence)),
                record,
            )

            return record

        return create_record(transaction)

    def save_record(self, record: dict) -> dict:
        """Save an existing record."""

        self._check_record(record)

        if self.use_cloud:
            db = self._client()

            db.collection(self.collection_name).document(
                str(record["sequence"])
            ).set(record)

        else:
            records = self.read_chain()
            records.append(record)

            records.sort(
                key=lambda item: item["sequence"]
            )

            self.local_path.write_text(
                json.dumps(records, indent=2),
                encoding="utf-8",
            )

        return {
            "status": "stored",
            "mode": self.mode,
            "sequence": record.get("sequence"),
        }

    def read_chain(self) -> list[dict]:
        """Read all records in ascending sequence order."""

        if self.use_cloud:
            db = self._client()

            docs = (
                db.collection(self.collection_name)
                .order_by("sequence")
                .stream()
            )

            return [doc.to_dict() for doc in docs]

        records = json.loads(
            self.local_path.read_text(encoding="utf-8")
        )

        return sorted(
            records,
            key=lambda item: item.get("sequence", 0),
        )

    def get_records(self) -> list[dict]:
        """Return all ledger records."""

        return self.read_chain()

    def allocate_sequence(self) -> int:
        """Legacy counter helper; add_event uses an atomic transaction."""

        if not self.use_cloud:
            return len(self.read_chain()) + 1

        from google.cloud import firestore

        db = self._client()

        counter_ref = db.collection(
            self.metadata_collection_name
        ).document("sequence_counter")

        transaction = db.transaction()

        @firestore.transactional
        def update_counter(txn):
            snapshot = counter_ref.get(transaction=txn)

            current = (
                snapshot.get("value")
                if snapshot.exists
                else 0
            )

            next_value = current + 1

            txn.set(
                counter_ref,
                {"value": next_value},
            )

            return next_value

        return update_counter(transaction)

    def save_checkpoint(self, checkpoint: dict) -> None:
        """Persist the latest trusted checkpoint."""

        if self.use_cloud:
            db = self._client()

            db.collection(self.metadata_collection_name).document(
                "checkpoint"
            ).set(checkpoint)

        else:
            self.checkpoint_path.write_text(
                json.dumps(checkpoint, indent=2),
                encoding="utf-8",
            )

    def get_checkpoint(self) -> dict[str, Any] | None:
        """Retrieve the persisted checkpoint."""

        if self.use_cloud:
            db = self._client()

            snapshot = (
                db.collection(self.metadata_collection_name)
                .document("checkpoint")
                .get()
            )

            return snapshot.to_dict() if snapshot.exists else None

        if not self.checkpoint_path.exists():
            return None

        return json.loads(
            self.checkpoint_path.read_text(encoding="utf-8")
        )
