from __future__ import annotations

import unittest

from app.ledger_core import AuditLedger


EVENT_ONE = {
    "event_type": "access",
    "actor_id": "actor-demo-01",
    "action": "viewed synthetic record",
    "resource_id": "resource-demo-01",
    "outcome": "success",
}

EVENT_TWO = {
    "event_type": "configuration",
    "actor_id": "actor-demo-02",
    "action": "changed synthetic setting",
    "resource_id": "resource-demo-02",
    "outcome": "success",
}


class AuditLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = AuditLedger()
        self.ledger.add_event(EVENT_ONE)
        self.ledger.add_event(EVENT_TWO)

    def test_t01_untouched_chain_verifies(self) -> None:
        result = self.ledger.verify_records(self.ledger.get_records())
        self.assertTrue(result["valid"])
        self.assertEqual(2, result["checked_records"])

    def test_t02_changed_event_is_detected(self) -> None:
        records = self.ledger.get_records()
        records[0]["action"] = "tampered value"
        result = self.ledger.verify_records(records)
        self.assertFalse(result["valid"])
        self.assertEqual(1, result["failed_sequence"])

    def test_t03_reordered_event_is_detected(self) -> None:
        records = list(reversed(self.ledger.get_records()))
        result = self.ledger.verify_records(records)
        self.assertFalse(result["valid"])
        self.assertEqual(2, result["failed_sequence"])

    def test_t03_missing_event_is_detected(self) -> None:
        records = self.ledger.get_records()[1:]
        result = self.ledger.verify_records(records)
        self.assertFalse(result["valid"])
        self.assertEqual(2, result["failed_sequence"])

    def test_record_uses_frontend_contract_hash_name(self) -> None:
        record = self.ledger.get_records()[0]
        self.assertIn("current_hash", record)
        self.assertNotIn("hash", record)


if __name__ == "__main__":
    unittest.main()
