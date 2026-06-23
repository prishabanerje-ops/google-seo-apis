import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import psi


class TestValidateUrl(unittest.TestCase):
    def test_accepts_valid_https_url(self):
        self.assertEqual(psi.validate_url("https://example.com"), "https://example.com")

    def test_accepts_https_with_path(self):
        self.assertEqual(
            psi.validate_url("https://example.com/page"),
            "https://example.com/page"
        )

    def test_rejects_localhost(self):
        with self.assertRaises(ValueError):
            psi.validate_url("http://localhost/test")

    def test_rejects_private_ip_10(self):
        with self.assertRaises(ValueError):
            psi.validate_url("http://10.0.0.1/")

    def test_rejects_private_ip_192_168(self):
        with self.assertRaises(ValueError):
            psi.validate_url("http://192.168.1.1/")

    def test_rejects_loopback_127(self):
        with self.assertRaises(ValueError):
            psi.validate_url("http://127.0.0.1/")

    def test_rejects_missing_scheme(self):
        with self.assertRaises(ValueError):
            psi.validate_url("example.com")


class TestFormatScore(unittest.TestCase):
    def test_good_score_90_plus(self):
        result = psi.format_score(0.90)
        self.assertIn("✓ Good", result)
        self.assertIn("90", result)

    def test_needs_improvement_50_to_89(self):
        result = psi.format_score(0.72)
        self.assertIn("⚠ Needs Improvement", result)

    def test_poor_score_below_50(self):
        result = psi.format_score(0.45)
        self.assertIn("✗ Poor", result)


class TestRateCwv(unittest.TestCase):
    def test_lcp_good(self):
        self.assertEqual(psi.rate_cwv("lcp", 2000), "✓ Good")

    def test_lcp_needs_improvement(self):
        self.assertEqual(psi.rate_cwv("lcp", 3000), "⚠ Needs Improvement")

    def test_lcp_poor(self):
        self.assertEqual(psi.rate_cwv("lcp", 4500), "✗ Poor")

    def test_inp_good(self):
        self.assertEqual(psi.rate_cwv("inp", 150), "✓ Good")

    def test_inp_poor(self):
        self.assertEqual(psi.rate_cwv("inp", 600), "✗ Poor")

    def test_cls_good(self):
        self.assertEqual(psi.rate_cwv("cls", 0.05), "✓ Good")

    def test_cls_poor(self):
        self.assertEqual(psi.rate_cwv("cls", 0.30), "✗ Poor")

    def test_fcp_good(self):
        self.assertEqual(psi.rate_cwv("fcp", 1500), "✓ Good")


class TestRunPsi(unittest.TestCase):
    def _mock_urlopen(self, data: dict):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(data).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_returns_parsed_json(self):
        fake = {"lighthouseResult": {"categories": {}}, "loadingExperience": {}}
        with patch('urllib.request.urlopen', return_value=self._mock_urlopen(fake)):
            result = psi.run_psi("https://example.com", "mobile", None)
        self.assertIn("lighthouseResult", result)

    def test_api_key_included_in_request_url(self):
        fake = {"lighthouseResult": {"categories": {}}, "loadingExperience": {}}
        with patch('urllib.request.urlopen', return_value=self._mock_urlopen(fake)) as mock_open:
            psi.run_psi("https://example.com", "mobile", "test-key-abc")
            called_url = mock_open.call_args[0][0]
            self.assertIn("test-key-abc", called_url)

    def test_strategy_included_in_request_url(self):
        fake = {"lighthouseResult": {"categories": {}}, "loadingExperience": {}}
        with patch('urllib.request.urlopen', return_value=self._mock_urlopen(fake)) as mock_open:
            psi.run_psi("https://example.com", "desktop", None)
            called_url = mock_open.call_args[0][0]
            self.assertIn("desktop", called_url)


if __name__ == '__main__':
    unittest.main()
