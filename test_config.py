#!/usr/bin/env python3
"""TDD tests for config.py - RED phase first."""

import os
import sys
import unittest

# RED: Import will fail because config.py doesn't exist yet
try:
    import config
except ImportError:
    config = None


class TestConfigLoading(unittest.TestCase):
    """Test config.yaml loading."""

    def test_config_module_exists(self):
        """Config module should exist."""
        if config is None:
            self.fail("RED phase: config module not yet created")
        self.assertIsNotNone(config, "config module should exist")

    def test_load_config_returns_dict(self):
        """load_config() should return a dict with config values."""
        if config is None:
            self.fail("RED phase: config module not yet created")

        # This will fail because load_config() doesn't exist yet
        result = config.load_config()
        self.assertIsInstance(result, dict)

    def test_config_has_required_fields(self):
        """Config should have all required fields."""
        if config is None:
            self.fail("RED phase: config module not yet created")

        cfg = config.load_config()
        required_fields = [
            'graalvm_file_id', 'versions_file_id', 'python_portable_file_id',
            'tlauncher_url', 'java_dest_root', 'otp_timeout_seconds'
        ]
        for field in required_fields:
            self.assertIn(field, cfg, f"Config missing field: {field}")


if __name__ == '__main__':
    unittest.main()
