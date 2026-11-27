import json, os
from pathlib import Path

class LedgerStorageAdapter:
    def __init__(self, use_cloud: bool = False, local_path: str = "data/local_ledger.json"):
        self.use_cloud = use_cloud and os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"
        self.mode = "GCP_FIRESTORE" if self.use_cloud else "LOCAL_SIMULATION"
        self.local_path = Path(local_path)
        if not self.use_cloud:
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.local_path.exists():
                self.local_path.write_text("[]", encoding="utf-8")

    def save_record(self, record: dict) -> dict:
        if "PRIVATE KEY" in json.dumps(record):
            raise ValueError("SECURITY_BLOCK: Private key material must never be stored in audit records.")
        if self.use_cloud:
            from google.cloud import firestore
            db = firestore.Client()
            db.collection(os.getenv("FIRESTORE_COLLECTION", "audit_ledger")).document(str(record["sequence"])).set(record)
        else:
            records = self.read_chain()
            records.append(record)
            self.local_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return {"status": "stored", "mode": self.mode, "sequence": record.get("sequence")}

    def read_chain(self) -> list:
        if self.use_cloud:
            from google.cloud import firestore
            db = firestore.Client()
            docs = db.collection(os.getenv("FIRESTORE_COLLECTION", "audit_ledger")).order_by("sequence").stream()
            return [d.to_dict() for d in docs]
        records = json.loads(self.local_path.read_text(encoding="utf-8"))
        return sorted(records, key=lambda r: r.get("sequence", 0))
