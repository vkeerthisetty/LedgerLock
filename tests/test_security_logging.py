
import unittest

from app.security_logging import sanitise_log_fields


class SecurityLoggingTests(unittest.TestCase):

    def test_approved_fields_are_preserved(self):
        result = sanitise_log_fields({
            "event_type": "authentication",
            "outcome": "success",
        })
        self.assertEqual(
            {"event_type": "authentication", "outcome": "success"},
            result,
        )

    def test_unapproved_fields_are_removed(self):
        result = sanitise_log_fields({
            "password": "secret123",
            "private_key": "test-key",
            "event_type": "access",
        })
        self.assertEqual({"event_type": "access"}, result)

    def test_free_form_sensitive_values_are_rejected(self):
        result = sanitise_log_fields({
            "event_type": "Bearer_SECRET_TOKEN",
        })
        self.assertEqual({}, result)

    def test_non_string_values_are_rejected(self):
        result = sanitise_log_fields({
            "event_type": ["sensitive", "data"],
        })
        self.assertEqual({}, result)


if __name__ == "__main__":
    unittest.main()
