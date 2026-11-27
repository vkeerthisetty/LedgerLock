from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import api as api_module
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
        app.state.checkpoint = None

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

    def test_checkpoint_requires_admin_token(self) -> None:
        response = self.client.post("/api/checkpoints")

        self.assertEqual(403, response.status_code)
        self.assertNotIn("Not authorised", response.text)

    def test_create_and_verify_local_checkpoint(self) -> None:
        old_token = api_module.ADMIN_TOKEN
        old_secret = api_module.CHECKPOINT_SECRET
        api_module.ADMIN_TOKEN = "synthetic-admin-token"
        api_module.CHECKPOINT_SECRET = "x" * 32

        try:
            created = self.client.post("/api/events", json=VALID_EVENT)
            self.assertEqual(201, created.status_code)

            checkpoint = self.client.post(
                "/api/checkpoints",
                headers={"x-admin-token": "synthetic-admin-token"},
            )
            self.assertEqual(200, checkpoint.status_code)
            self.assertEqual("created", checkpoint.json()["status"])

            verified = self.client.post("/api/verify")
            self.assertEqual(200, verified.status_code)
            self.assertTrue(verified.json()["valid"])
            self.assertTrue(verified.json()["checkpoint_valid"])
            self.assertEqual(
                "Chain and checkpoint verified.",
                verified.json()["message"],
            )
        finally:
            api_module.ADMIN_TOKEN = old_token
            api_module.CHECKPOINT_SECRET = old_secret


if __name__ == "__main__":
    unittest.main()
