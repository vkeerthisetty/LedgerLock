
from __future__ import annotations

import os
import unittest

os.environ.setdefault("LEDGERLOCK_API_MODE", "mock")

from fastapi import Body, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import app


class TestPayload(BaseModel):
    age: int


class AppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(
            app,
            raise_server_exceptions=False,
        )

    def setUp(self) -> None:
        app.state.ledger.clear()

    def test_health_is_safe_and_explicit(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "status": "ok",
                "service": "ledgerlock-api",
                "environment": "development",
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

    def test_http_error_does_not_expose_internal_detail(self) -> None:
        response = self.client.get("/missing-private-resource")

        self.assertEqual(404, response.status_code)
        self.assertEqual(
            {
                "error": {
                    "code": "http_error",
                    "message": "The requested resource was not found.",
                }
            },
            response.json(),
        )

    def test_unexpected_error_does_not_expose_exception_details(self) -> None:

        @app.get("/test-internal-error")
        async def internal_error():
            raise RuntimeError("SECRET_PRIVATE_KEY_TEST_VALUE")

        try:
            response = self.client.get("/test-internal-error")

            self.assertEqual(500, response.status_code)
            self.assertNotIn(
                "SECRET_PRIVATE_KEY_TEST_VALUE",
                response.text,
            )
            self.assertNotIn("Traceback", response.text)
            self.assertEqual(
                "internal_error",
                response.json()["error"]["code"],
            )
        finally:
            app.router.routes[:] = [
                route for route in app.router.routes
                if getattr(route, "path", None) != "/test-internal-error"
            ]

    def test_validation_error_does_not_expose_submitted_values(self) -> None:

        @app.post("/test-validation")
        async def test_validation(
            payload: TestPayload = Body(embed=False),
        ):
            return {"status": "ok"}

        try:
            response = self.client.post(
                "/test-validation",
                json={"age": "SECRET_TEST_VALUE"},
            )

            self.assertEqual(422, response.status_code)
            self.assertNotIn("SECRET_TEST_VALUE", response.text)
            self.assertEqual(
                "validation_error",
                response.json()["error"]["code"],
            )
            self.assertEqual(
                ["age"],
                response.json()["error"]["fields"],
            )
        finally:
            app.router.routes[:] = [
                route for route in app.router.routes
                if getattr(route, "path", None) != "/test-validation"
            ]


if __name__ == "__main__":
    unittest.main()
