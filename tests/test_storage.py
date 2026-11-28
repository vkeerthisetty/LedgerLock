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

                # Simulate a new storage instance after restart.
                second_storage = LedgerStorageAdapter(use_cloud=False)

                self.assertEqual(
                    second_storage.get_checkpoint(),
                    checkpoint,
                )


if __name__ == "__main__":
    unittest.main()
