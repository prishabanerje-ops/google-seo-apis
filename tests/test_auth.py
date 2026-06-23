import json
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import auth


# ---------------------------------------------------------------------------
# Existing tests (unchanged behaviourally)
# ---------------------------------------------------------------------------

class TestGetApiKey(unittest.TestCase):
    def test_returns_key_from_config_file(self):
        with patch('auth._load_config', return_value={"api_key": "test-key-123"}):
            self.assertEqual(auth.get_api_key(), "test-key-123")

    def test_falls_back_to_env_var(self):
        with patch('auth._load_config', return_value={}):
            with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key-456"}):
                self.assertEqual(auth.get_api_key(), "env-key-456")

    def test_returns_none_when_not_configured(self):
        with patch('auth._load_config', return_value={}):
            env = {k: v for k, v in os.environ.items() if k != "GOOGLE_API_KEY"}
            with patch.dict(os.environ, env, clear=True):
                self.assertIsNone(auth.get_api_key())


class TestGetGscProperty(unittest.TestCase):
    def test_returns_property_from_config(self):
        with patch('auth._load_config', return_value={"gsc_property": "sc-domain:example.com"}):
            self.assertEqual(auth.get_gsc_property(), "sc-domain:example.com")

    def test_falls_back_to_env_var(self):
        with patch('auth._load_config', return_value={}):
            with patch.dict(os.environ, {"GSC_PROPERTY": "sc-domain:example.com"}):
                self.assertEqual(auth.get_gsc_property(), "sc-domain:example.com")


class TestLoadConfig(unittest.TestCase):
    def test_loads_valid_json_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"api_key": "abc"}, f)
            tmp_path = f.name
        with patch('auth.CONFIG_PATH', tmp_path):
            config = auth._load_config()
        os.unlink(tmp_path)
        self.assertEqual(config["api_key"], "abc")

    def test_returns_empty_dict_when_file_missing(self):
        with patch('auth.CONFIG_PATH', '/nonexistent/path/config.json'):
            self.assertEqual(auth._load_config(), {})


# ---------------------------------------------------------------------------
# New OAuth tests
# ---------------------------------------------------------------------------

class TestGetOauthClientPath(unittest.TestCase):
    def test_returns_path_from_config(self):
        with patch('auth._load_config', return_value={"oauth_client_path": "/home/user/client_secret.json"}):
            env = {k: v for k, v in os.environ.items() if k != "OAUTH_CLIENT_PATH"}
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(auth.get_oauth_client_path(), "/home/user/client_secret.json")

    def test_returns_path_from_env_var(self):
        with patch('auth._load_config', return_value={}):
            with patch.dict(os.environ, {"OAUTH_CLIENT_PATH": "/env/client_secret.json"}):
                self.assertEqual(auth.get_oauth_client_path(), "/env/client_secret.json")

    def test_returns_none_when_not_configured(self):
        with patch('auth._load_config', return_value={}):
            env = {k: v for k, v in os.environ.items() if k != "OAUTH_CLIENT_PATH"}
            with patch.dict(os.environ, env, clear=True):
                self.assertIsNone(auth.get_oauth_client_path())


class TestGetGscCredentials(unittest.TestCase):
    def test_returns_none_when_no_token(self):
        with patch('auth._load_oauth_token', return_value=None):
            result = auth.get_gsc_credentials()
        self.assertIsNone(result)

    def test_loads_valid_token(self):
        future_expiry = time.time() + 3600
        token_data = {
            "access_token": "ya29.test",
            "refresh_token": "1//test_refresh",
            "expires_at": future_expiry,
            "client_id": "client-id-123.apps.googleusercontent.com",
        }
        mock_client_data = {
            "client_id": "client-id-123.apps.googleusercontent.com",
            "client_secret": "GOCSPX-secret",
        }
        mock_creds = MagicMock()

        # Credentials is imported lazily inside get_gsc_credentials, so we
        # patch it at its source module rather than on `auth`.
        with patch('auth._load_oauth_token', return_value=token_data), \
             patch('auth.get_oauth_client_path', return_value="/fake/client_secret.json"), \
             patch('auth._load_oauth_client', return_value=mock_client_data), \
             patch('google.oauth2.credentials.Credentials', return_value=mock_creds) as MockCreds:
            result = auth.get_gsc_credentials()

        MockCreds.assert_called_once_with(
            token="ya29.test",
            refresh_token="1//test_refresh",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client-id-123.apps.googleusercontent.com",
            client_secret="GOCSPX-secret",
        )
        self.assertEqual(result, mock_creds)

    def test_refreshes_expired_token(self):
        past_expiry = time.time() - 100  # already expired
        token_data = {
            "access_token": "ya29.old",
            "refresh_token": "1//refresh",
            "expires_at": past_expiry,
            "client_id": "client-id.apps.googleusercontent.com",
        }
        refreshed_token = {
            "access_token": "ya29.new",
            "refresh_token": "1//refresh",
            "expires_at": time.time() + 3600,
            "client_id": "client-id.apps.googleusercontent.com",
        }
        mock_client_data = {
            "client_id": "client-id.apps.googleusercontent.com",
            "client_secret": "GOCSPX-secret",
        }
        mock_creds = MagicMock()

        with patch('auth._load_oauth_token', return_value=token_data), \
             patch('auth.get_oauth_client_path', return_value="/fake/client_secret.json"), \
             patch('auth._load_oauth_client', return_value=mock_client_data), \
             patch('auth._refresh_oauth_token', return_value=refreshed_token) as mock_refresh, \
             patch('google.oauth2.credentials.Credentials', return_value=mock_creds):
            result = auth.get_gsc_credentials()

        mock_refresh.assert_called_once_with(mock_client_data, token_data)
        self.assertEqual(result, mock_creds)


class TestCheckOutput(unittest.TestCase):
    def test_check_shows_oauth_not_service_account(self):
        """--check output must mention OAuth token, not service account."""
        import io
        future_expiry = time.time() + 86400
        token_data = {
            "access_token": "ya29.test",
            "expires_at": future_expiry,
        }

        with patch('auth.get_api_key', return_value="AIzaSy-test"), \
             patch('auth._load_oauth_token', return_value=token_data), \
             patch('auth.get_gsc_property', return_value="sc-domain:example.com"), \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            auth._check()

        output = mock_stdout.getvalue()
        self.assertIn("OAuth token", output)
        self.assertNotIn("Service Account", output)
        self.assertNotIn("service account", output)
        self.assertIn("✓ OK", output)


if __name__ == '__main__':
    unittest.main()
