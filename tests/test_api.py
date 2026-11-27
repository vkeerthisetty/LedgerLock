from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app


VALID_EVENT = {
    "event_type": "access",
    "actor_id": "actor-demo-01",
    "action": "viewed synthetic record",
    "resource_id": "resource-demo-01",
    "outcome": "success",
}


class LedgerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def setUp(self) -> None:
        app.state.ledger.clear()

    def test_create_list_and_verify_chain(self) -> None:
        created = self.client.post("/api/events", json=VALID_EVENT)
        self.assertEqual(201, created.status_code)
        self.assertEqual(1, created.json()["sequence"])
        self.assertIn("current_hash", created.json())

        listed = self.client.get("/api/ledger")
        self.assertEqual(200, listed.status_code)
        self.assertEqual(1, listed.json()["count"])
        self.assertEqual("unavailable", listed.json()["checkpoint"]["status"])

        verified = self.client.post("/api/verify")
        self.assertEqual(200, verified.status_code)
        self.assertTrue(verified.json()["valid"])
        self.assertFalse(verified.json()["checkpoint_valid"])
        self.assertIn("unavailable", verified.json()["message"].lower())

    def test_validation_error_is_stable_and_does_not_echo_input(self) -> None:
        payload = {**VALID_EVENT, "actor_id": "<private-test-value>", "outcome": "bad"}
        response = self.client.post("/api/events", json=payload)
        self.assertEqual(422, response.status_code)
        self.assertEqual("Request validation failed.", response.json()["message"])
        self.assertNotIn("private-test-value", response.text)

    def test_extra_fields_are_rejected_without_echoing_values(self) -> None:
        payload = {**VALID_EVENT, "secret": "do-not-echo"}
        response = self.client.post("/api/events", json=payload)
        self.assertEqual(422, response.status_code)
        self.assertNotIn("do-not-echo", response.text)


if __name__ == "__main__":
    unittest.main()
