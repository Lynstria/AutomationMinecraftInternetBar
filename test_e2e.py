#!/usr/bin/env python3
"""E2E test for AutomationMinecraftInternetBar.
Tests the full flow with fixtures. Saves temp files to test_fixtures/.
"""

import os
import sys
import unittest
import tempfile
import json
import subprocess
from unittest.mock import patch
from crypto_utils import derive_key, SALT_SIZE, OLD_SALT
from cryptography.fernet import Fernet

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_fixtures')
SECRETS_ENC_PATH = os.path.join(TEST_DIR, 'secrets.enc')
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/test_e2e"
GOOGLE_CREDS = '{"client_id": "test", "client_secret": "test"}'


def create_test_fixture():
    """Create test_fixtures: secrets.enc with known password (new format with salt prefix)."""
    os.makedirs(TEST_DIR, exist_ok=True)

    # Create secrets.enc with password "test123" - new format (salt + encrypted)
    password = "test123"
    salt = os.urandom(16)  # Random salt
    key = derive_key(password, salt)
    f = Fernet(key)
    decrypted = DISCORD_WEBHOOK + "\n" + GOOGLE_CREDS
    encrypted = f.encrypt(decrypted.encode('utf-8'))
    with open(SECRETS_ENC_PATH, 'wb') as out:
        out.write(salt + encrypted)  # New format: salt prefix

    return password


class TestE2EFlow(unittest.TestCase):
    """Test the full E2E flow."""

    @classmethod
    def setUpClass(cls):
        cls.password = create_test_fixture()

    def test_decrypt_secrets_returns_valid_json(self):
        """Run decrypt_secrets.py and verify JSON output."""
        # decrypt_secrets.py is in .vscode/ directory
        decrypt_script = os.path.join(os.path.dirname(__file__), '.vscode', 'decrypt_secrets.py')
        # Pass password as command-line argument
        result = subprocess.run(
            [sys.executable, decrypt_script, SECRETS_ENC_PATH, self.password],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )

        # stdout should be pure JSON
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"stdout is not valid JSON: {result.stdout}")

        # Verify structure
        self.assertIn("discord_webhook", output)
        self.assertIn("google_credentials_path", output)
        self.assertEqual(output["discord_webhook"], DISCORD_WEBHOOK)

        # Verify credentials file exists
        cred_path = output["google_credentials_path"]
        self.assertTrue(os.path.exists(cred_path), f"Credentials file not found: {cred_path}")

        # Clean up credentials file
        if os.path.exists(cred_path):
            os.unlink(cred_path)

    def test_config_loading(self):
        """Verify config.yaml is loaded correctly."""
        from config import load_config
        cfg = load_config()
        self.assertIsInstance(cfg, dict)
        required = ['graalvm_file_id', 'versions_file_id', 'python_portable_file_id',
                    'tlauncher_url', 'java_dest_root', 'otp_timeout_seconds']
        for field in required:
            self.assertIn(field, cfg, f"Config missing field: {field}")

    def test_crypto_utils_decrypt(self):
        """Test crypto_utils.decrypt_secrets_file() directly."""
        from crypto_utils import decrypt_secrets_file
        result = decrypt_secrets_file(SECRETS_ENC_PATH, self.password)
        self.assertIn("discord_webhook", result)
        self.assertIn("google_credentials_json", result)
        self.assertEqual(result["discord_webhook"], DISCORD_WEBHOOK)


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        # Clean up test fixtures
        if os.path.exists(SECRETS_ENC_PATH):
            os.unlink(SECRETS_ENC_PATH)
        # Remove test_fixtures dir if empty
        try:
            os.rmdir(TEST_DIR)
        except:
            pass
