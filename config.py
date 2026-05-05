#!/usr/bin/env python3
"""Config loader for AutomationMinecraftInternetBar."""

import os
import yaml


def load_config():
    """Load config from config.yaml in the same directory."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
