import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import auth


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


class TestGetServiceAccountPath(unittest.TestCase):
    def test_returns_path_from_config(self):
        with patch('auth._load_config', return_value={"service_account_path": "/tmp/sa.json"}):
            self.assertEqual(auth.get_service_account_path(), "/tmp/sa.json")

    def test_falls_back_to_env_var(self):
        with patch('auth._load_config', return_value={}):
            with patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/tmp/sa.json"}):
                self.assertEqual(auth.get_service_account_path(), "/tmp/sa.json")

    def test_returns_none_when_not_configured(self):
        with patch('auth._load_config', return_value={}):
            env = {k: v for k, v in os.environ.items() if k != "GOOGLE_APPLICATION_CREDENTIALS"}
            with patch.dict(os.environ, env, clear=True):
                self.assertIsNone(auth.get_service_account_path())


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


if __name__ == '__main__':
    unittest.main()
