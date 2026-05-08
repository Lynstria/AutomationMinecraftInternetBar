"""CustomCore.py - Write java config to .tlauncher folder.
# -*- coding: utf-8 -*-
Stdlib only: json, os.
"""

import os
import json


def setup_logging():
    """Setup logging. Read log path from %TEMP%\mc_log_path.txt."""
    import logging
    log_path_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "mc_log_path.txt")
    if os.path.exists(log_path_file):
        with open(log_path_file, encoding="utf-8-sig") as f:
            log_file = f.read().strip()
    else:
        log_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "custom_core.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


def read_java_config(json_path):
    """Read minecraft_tlauncher_java_config.json. Return dict or None."""
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def find_tlauncher_folder(search_root=None):
    """Find .tlauncher folder (case-insensitive) in AppData.
    Search order: APPDATA (Roaming), then LOCALAPPDATA.
    Return full path or None."""
    if search_root:
        folders = [search_root]
    else:
        folders = []
        for env_var in ["APPDATA", "LOCALAPPDATA"]:
            path = os.environ.get(env_var)
            if path:
                folders.append(path)

    for root in folders:
        if not os.path.isdir(root):
            continue
        for entry in os.listdir(root):
            full = os.path.join(root, entry)
            if os.path.isdir(full) and entry.lower() == ".tlauncher":
                return full
    return None


def write_java_config(config, dest_dir=None):
    """Write java config JSON to .tlauncher folder.
    If dest_dir provided, use it. Otherwise find .tlauncher folder.
    Return True on success."""
    if dest_dir is None:
        dest_dir = find_tlauncher_folder()
    if not dest_dir:
        return False

    config_path = os.path.join(dest_dir, "minecraft_tlauncher_java_config.json")
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def run_custom_core():
    """Main entry point. Read config, write to .tlauncher folder."""
    logger = setup_logging()
    logger.info("Starting CustomCore.py")

    # Read config from same directory as script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "minecraft_tlauncher_java_config.json")

    config = read_java_config(config_path)
    if not config:
        logger.error("Failed to read java config: %s", config_path)
        return False

    logger.info("Java config read: %s", config)

    # Write to .tlauncher folder
    ok = write_java_config(config)
    if ok:
        logger.info("Java config written to .tlauncher folder")
    else:
        logger.error("Failed to write java config")

    return ok


if __name__ == "__main__":
    run_custom_core()
