from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryFoundationTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_required_foundation_files_exist(self) -> None:
        required = {
            ".env.example",
            ".gitignore",
            ".github/pull_request_template.md",
            ".github/workflows/ci.yml",
            "app/main.py",
            "app/templates/index.html",
            "app/static/css/styles.css",
            "app/static/js/app.js",
            "docs/api-contract.md",
            "docs/frontend-acceptance.md",
            "docs/integration-checklist.md",
        }
        missing = sorted(path for path in required if not (ROOT / path).is_file())
        self.assertEqual([], missing, f"Missing required files: {missing}")

    def test_frontend_contains_required_workflow_regions(self) -> None:
        html = self.read("app/templates/index.html")
        required_ids = {
            "event-form",
            "ledger-body",
            "verify-button",
            "chain-status",
            "verification-result",
            "mock-warning",
            "demo-controls",
        }
        present_ids = set(re.findall(r'id="([^"]+)"', html))
        self.assertTrue(required_ids.issubset(present_ids), required_ids - present_ids)

    def test_frontend_uses_agreed_api_routes(self) -> None:
        javascript = self.read("app/static/js/app.js")
        for route in ("/api/events", "/api/ledger", "/api/verify"):
            self.assertIn(route, javascript)

    def test_mock_mode_is_explicitly_disclaimed(self) -> None:
        html = self.read("app/templates/index.html").lower()
        readme = self.read("README.md").lower()
        self.assertIn("frontend preview only", html)
        self.assertIn("not cryptographic or cloud-integration evidence", readme)

    def test_gitignore_blocks_common_secret_files(self) -> None:
        gitignore = self.read(".gitignore")
        for pattern in (".env", "*.pem", "*.key", "*service-account*.json"):
            self.assertIn(pattern, gitignore)

    def test_env_example_contains_no_obvious_secret_assignment(self) -> None:
        env_example = self.read(".env.example")
        forbidden = re.compile(r"(?im)^(password|token|secret|private_key)\s*=\s*\S+")
        self.assertIsNone(forbidden.search(env_example))


if __name__ == "__main__":
    unittest.main()
