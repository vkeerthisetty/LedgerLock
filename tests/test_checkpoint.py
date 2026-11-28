
import unittest

from app.checkpoint import create_checkpoint, verify_checkpoint


class CheckpointTests(unittest.TestCase):

    def setUp(self):
        self.secret = "development-test-secret-" + ("x" * 32)

        self.records = [
            {"sequence": 1, "current_hash": "hash-one"},
            {"sequence": 2, "current_hash": "hash-two"},
            {"sequence": 3, "current_hash": "hash-three"},
        ]

    def test_valid_checkpoint(self):
        checkpoint = create_checkpoint(self.records, self.secret)
        self.assertTrue(
            verify_checkpoint(self.records, checkpoint, self.secret)
        )

    def test_detects_deleted_final_record(self):
        checkpoint = create_checkpoint(self.records, self.secret)
        shortened_records = self.records[:-1]

        self.assertFalse(
            verify_checkpoint(shortened_records, checkpoint, self.secret)
        )

    def test_detects_modified_latest_hash(self):
        checkpoint = create_checkpoint(self.records, self.secret)
        modified_records = [dict(record) for record in self.records]
        modified_records[-1]["current_hash"] = "changed-hash"

        self.assertFalse(
            verify_checkpoint(modified_records, checkpoint, self.secret)
        )

    def test_detects_modified_checkpoint_signature(self):
        checkpoint = create_checkpoint(self.records, self.secret)
        checkpoint["signature"] = "invalid-signature"

        self.assertFalse(
            verify_checkpoint(self.records, checkpoint, self.secret)
        )

    def test_wrong_secret_fails(self):
        checkpoint = create_checkpoint(self.records, self.secret)

        self.assertFalse(
            verify_checkpoint(
                self.records,
                checkpoint,
                "a-different-secret-" + ("y" * 32),
            )
        )

    def test_empty_ledger_checkpoint(self):
        checkpoint = create_checkpoint([], self.secret)
        self.assertTrue(
            verify_checkpoint([], checkpoint, self.secret)
        )


if __name__ == "__main__":
    unittest.main()
