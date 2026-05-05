#!/usr/bin/env python3
"""TDD tests for mc_utils.py - Full cycle."""

import os
import sys
import tempfile
import shutil
import unittest
import mc_utils


class TestFindMinecraftDir(unittest.TestCase):
    """Test find_minecraft_dir() behavior."""

    def setUp(self):
        """Create a temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

        # Save original env vars
        self.orig_appdata = os.environ.get('APPDATA')
        self.orig_localappdata = os.environ.get('LOCALAPPDATA')
        self.orig_userprofile = os.environ.get('USERPROFILE')

    def tearDown(self):
        """Restore original env vars."""
        for var, val in [('APPDATA', self.orig_appdata),
                          ('LOCALAPPDATA', self.orig_localappdata),
                          ('USERPROFILE', self.orig_userprofile)]:
            if val is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = val

    def _set_env_to_temp(self, subdir=''):
        """Set all relevant env vars to temp directory."""
        appdata = os.path.join(self.temp_dir, 'AppData', 'Roaming')
        localappdata = os.path.join(self.temp_dir, 'AppData', 'Local')
        userprofile = os.path.join(self.temp_dir, 'Users', 'TestUser')

        os.makedirs(appdata, exist_ok=True)
        os.makedirs(localappdata, exist_ok=True)
        os.makedirs(userprofile, exist_ok=True)

        os.environ['APPDATA'] = appdata
        os.environ['LOCALAPPDATA'] = localappdata
        os.environ['USERPROFILE'] = userprofile

        return appdata

    def test_returns_path_when_tlauncher_legacy_game_exists(self):
        """When .tlauncher/legacy/Minecraft/game exists, return its path."""
        appdata = self._set_env_to_temp()

        game_path = os.path.join(appdata, '.tlauncher', 'legacy', 'Minecraft', 'game')
        os.makedirs(game_path)

        result = mc_utils.find_minecraft_dir()
        self.assertEqual(result, game_path)

    def test_returns_path_when_minecraft_dir_exists(self):
        """When .minecraft exists, return its path."""
        appdata = self._set_env_to_temp()

        mc_path = os.path.join(appdata, '.minecraft')
        os.makedirs(mc_path)

        result = mc_utils.find_minecraft_dir()
        self.assertEqual(result, mc_path)

    def test_raises_error_when_no_minecraft_found(self):
        """When no Minecraft dir exists, raise FileNotFoundError."""
        self._set_env_to_temp()

        with self.assertRaises(FileNotFoundError):
            mc_utils.find_minecraft_dir()


if __name__ == '__main__':
    unittest.main()
