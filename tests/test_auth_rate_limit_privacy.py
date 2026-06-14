from __future__ import annotations

import unittest

from ai_real_estate_fund.production.auth import APIKeyStore, hash_api_key
from ai_real_estate_fund.production.privacy import redact_payload, redact_text
from ai_real_estate_fund.production.rate_limit import InMemoryRateLimiter


class AuthRateLimitPrivacyTest(unittest.TestCase):
    def test_api_key_scopes(self) -> None:
        store = APIKeyStore.from_raw_keys(["analyst:secret-key:read|analyze"])
        self.assertTrue(store.verify("secret-key", required_scope="analyze").ok)
        self.assertFalse(store.verify("secret-key", required_scope="admin").ok)
        self.assertFalse(store.verify("wrong", required_scope="read").ok)
        self.assertEqual(len(hash_api_key("secret-key")), 64)

    def test_rate_limiter(self) -> None:
        limiter = InMemoryRateLimiter(limit=2, window_seconds=60)
        self.assertTrue(limiter.check("user").allowed)
        self.assertTrue(limiter.check("user").allowed)
        denied = limiter.check("user")
        self.assertFalse(denied.allowed)
        self.assertGreaterEqual(denied.retry_after_seconds, 0)

    def test_redaction(self) -> None:
        text = redact_text("Call 212-555-1212 or email person@example.com token=abcdefghi")
        self.assertIn("[redacted-phone]", text)
        self.assertIn("[redacted-email]", text)
        payload = redact_payload({"api_key": "secret", "nested": {"email": "a@b.com"}})
        self.assertEqual(payload["api_key"], "[redacted]")
        self.assertEqual(payload["nested"]["email"], "[redacted]")


if __name__ == "__main__":
    unittest.main()
