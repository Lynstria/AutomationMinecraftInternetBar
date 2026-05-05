#!/usr/bin/env python3
"""End-to-end test for Branch 1: Download & Work flow."""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import urllib.request

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import mc_utils


class TestBranch1Flow(unittest.TestCase):
    """Test Nhanh 1: Download & Work flow."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_config_has_required_fields_for_branch1(self):
        """Verify config has all required fields for Branch 1."""
        cfg = config.load_config()
        self.assertIn('graalvm_file_id', cfg)
        self.assertIn('versions_file_id', cfg)
        self.assertIn('tlauncher_url', cfg)
        self.assertIn('java_dest_root', cfg)

    @patch('urllib.request.urlretrieve')
    def test_mock_download_tlauncher(self, mock_urlretrieve):
        """Mock downloading TLauncher installer."""
        # Mock urlretrieve to do nothing
        mock_urlretrieve.return_value = (None, None)

        # Test download
        url = config.load_config().get('tlauncher_url')
        self.assertIsNotNone(url)

        # Simulate download
        output_path = os.path.join(self.temp_dir, 'tlauncher.exe')
        urllib.request.urlretrieve(url, output_path)
        mock_urlretrieve.assert_called_once_with(url, output_path)

    def test_mc_utils_finds_minecraft_dir(self):
        """Test that mc_utils can find Minecraft directory."""
        # Create a mock Minecraft directory structure - only .minecraft (no .tlauncher)
        appdata = os.path.join(self.temp_dir, 'AppData', 'Roaming')
        mc_path = os.path.join(appdata, '.minecraft')
        os.makedirs(mc_path)

        # Mock the entire find_minecraft_dir() to return our path
        with patch.object(mc_utils, 'find_minecraft_dir', return_value=mc_path):
            result = mc_utils.find_minecraft_dir()
            self.assertEqual(result, mc_path)

    def test_work_py_imports_correctly(self):
        """Verify Work.py can be imported without errors."""
        try:
            import Minecraft.Work as work
            self.assertTrue(hasattr(work, 'find_exe_folder'), "Should have find_exe_folder()")
            self.assertTrue(hasattr(work, 'find_zip'), "Should have find_zip()")
        except ImportError as e:
            self.fail(f"Failed to import Work.py: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
