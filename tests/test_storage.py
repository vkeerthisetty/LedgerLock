
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from storage.firestore_adapter import LedgerStorageAdapter


class StoragePersistenceTests(unittest.TestCase):

    def test_checkpoint_persists_after_restart(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_path = Path(temp_dir) / "checkpoint.json"

            with patch.dict(
                "os.environ",
                {
                    "USE_CLOUD_SERVICES": "false",
                    "LEDGERLOCK_LOCAL_CHECKPOINT_PATH": str(checkpoint_path),
                },
            ):
                first_storage = LedgerStorageAdapter(use_cloud=False)

                checkpoint = {
                    "latest_sequence": 3,
                    "latest_hash": "hash-three",
                    "signature": "test-signature",
                    "mode": "LOCAL_SIMULATION",
                }

                first_storage.save_checkpoint(checkpoint)

                second_storage = LedgerStorageAdapter(use_cloud=False)

                self.assertEqual(
                    second_storage.get_checkpoint(),
                    checkpoint,
                )

    def test_ledger_records_persist_after_restart(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "local_ledger.json"

            with patch.dict(
                "os.environ",
                {"USE_CLOUD_SERVICES": "false"},
            ):
                first_storage = LedgerStorageAdapter(
                    use_cloud=False,
                    local_path=str(ledger_path),
                )

                event = {
                    "event_type": "access",
                    "actor_id": "actor-demo-01",
                    "action": "viewed synthetic record",
                    "resource_id": "resource-demo-01",
                    "outcome": "success",
                }

                first_storage.add_event(event)

                second_storage = LedgerStorageAdapter(
                    use_cloud=False,
                    local_path=str(ledger_path),
                )

                restored_records = second_storage.get_records()

                self.assertEqual(len(restored_records), 1)
                self.assertEqual(restored_records[0]["sequence"], 1)
                self.assertEqual(
                    restored_records[0]["action"],
                    "viewed synthetic record",
                )
                self.assertIn("current_hash", restored_records[0])


if __name__ == "__main__":
    unittest.main()
