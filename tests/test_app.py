
from __future__ import annotations

import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("LEDGERLOCK_API_MODE", "mock")

from app.main import app  # noqa: E402
from app.ledger_core import AuditLedger  # noqa: E402


class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        app.state.ledger = AuditLedger()
        app.state.checkpoint = None
        self.client = TestClient(app)

    def test_health_is_safe_and_explicit(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "status": "ok",
                "service": "ledgerlock-frontend",
                "api_mode": "mock",
            },
            response.json(),
        )

    def test_dashboard_renders_mock_warning_and_core_regions(self) -> None:
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        body = response.text
        self.assertIn('data-api-mode="mock"', body)
        self.assertIn("Frontend preview only", body)
        self.assertIn('id="event-form"', body)
        self.assertIn('id="ledger-body"', body)
        self.assertIn('id="verify-button"', body)


if __name__ == "__main__":
    unittest.main()
